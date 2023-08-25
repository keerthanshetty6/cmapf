#include <sstream>
#include <set>
#include <optional>
#include <limits>

#include <clingo.hh>

#include "cmapf.h"

#define CMAPF_TRY try // NOLINT
#define CMAPF_CATCH catch (...){ Clingo::Detail::handle_cxx_error(); return false; } return true // NOLINT

namespace {

//! MAPF class for capturing MAPF problems.
class MAPF {
public:
    //! A node in the graph.
    struct Node {
        //! Construct a node with the given name.
        Node(Clingo::Symbol name) : name{name} { }

        //! The name of the node.
        Clingo::Symbol name;
        //! The outgoing edges of the node.
        std::vector<Node*> out;
        //! The incoming edges of the node.
        std::vector<Node*> in;
        //! The minimum time to reach this node from the start node.
        int cost = std::numeric_limits<int>::max();
        //! The maximum time point from which the goal can still be reached
        //! starting from this node.
        int max_cost = std::numeric_limits<int>::min();
        //! The time point from which this node cannot be entered anymore.
        int block = std::numeric_limits<int>::max();

    };
    //! Sort nodes in ascending order according to their cost.
    struct CostNodeCmp {
        bool operator()(Node *u, Node *v) const {
            if (u->cost != v->cost) {
                return u->cost < v->cost;
            }
            return u->name < v->name;
        }
    };
    //! Sort nodes in descending order according to their maximum cost.
    struct MaxCostNodeCmp {
        bool operator()(Node *u, Node *v) const {
            if (u->max_cost != v->max_cost) {
                return u->max_cost > v->max_cost;
            }
            return u->name < v->name;
        }
    };
    //! An agent in a MAPF problem.
    struct Agent {
        Agent(Clingo::Symbol name) : name{name} { }
        Clingo::Symbol name;
        Node *start = nullptr;
        Node *goal = nullptr;
        Clingo::Symbol sp_len = Clingo::Supremum();
    };
    //! Add a node with the given name to the MAPF problem.
    //!
    //! Returns the same node for the same name.
    Node *add_node(Clingo::Symbol u) {
        auto ins = node_map_.try_emplace(u, u);
        if (ins.second) {
            nodes_.emplace_back(&ins.first->second);
        }
        return &ins.first->second;
    }
    //! Add an agent with the given name to the MAPF problem.
    //!
    //! Returns the same node for the same name.
    Agent *add_agent(Clingo::Symbol a) {
        auto ins = agent_map_.try_emplace(a, a);
        if (ins.second) {
            agents_.emplace_back(&ins.first->second);
        }
        return &ins.first->second;
    }
    //! Add a start node for the given agent.
    void add_start(Clingo::Symbol a, Clingo::Symbol u) {
        add_agent(a)->start = add_node(u);
    }
    //! Add a goal node for the given agent.
    void add_goal(Clingo::Symbol a, Clingo::Symbol u) {
        add_agent(a)->goal = add_node(u);
    }
    //! Add an edge between two nodes.
    void add_edge(Clingo::Symbol u, Clingo::Symbol v) {
        auto *n_u = add_node(u);
        auto *n_v = add_node(v);
        n_u->out.emplace_back(n_v);
        n_v->in.emplace_back(n_u);
    }

    //! Initialize the problem from the given control object.
    void init(Clingo::Control &ctl) {
        auto syms = ctl.symbolic_atoms();
        for (auto it = syms.begin(Clingo::Signature{"start", 2}), ie = syms.end(); it != ie; ++it) {
            auto args = it->symbol().arguments();
            add_start(args.front(), args.back());
        }
        for (auto it = syms.begin(Clingo::Signature{"goal", 2}), ie = syms.end(); it != ie; ++it) {
            auto args = it->symbol().arguments();
            add_goal(args.front(), args.back());
        }
        for (auto it = syms.begin(Clingo::Signature{"edge", 2}), ie = syms.end(); it != ie; ++it) {
            auto args = it->symbol().arguments();
            add_edge(args.front(), args.back());
        }
    }

    //! Compute the length of the shortest paths between start and goal nodes
    //! of agents.
    //!
    //! A corresponding atom sp_length(A,L) is added to the given backend
    //! indicating that agent A can reach its goal within L time steps.
    //! Furthermore, the shortest path is stored for later use along with the
    //! agents.
    bool compute_sp(Clingo::Backend &bck) {
        for (auto *a : agents_) {
            if (!compute_sp_(a)) {
                return false;
            }
            auto atm = bck.add_atom(Clingo::Function("sp_length", {a->name, a->sp_len}));
            bck.rule(false, {atm}, {});
        }
        return true;
    }

    //! Compute a minmal delta for which the problem is not trivially
    //! unsatisfiable.
    std::optional<int> compute_min_delta() {
        for (auto *a : agents_) {
            if (!compute_sp_(a)) {
                return std::nullopt;
            }
        }

        for (int delta = 0;; ++delta) {
            bool stop = true;
            for (auto *a : agents_) {
                if (!compute_forward_reach_(a, delta)) {
                    stop = false;
                    break;
                }
            }
            if (stop) {
                return delta;
            }
        }
    }

    //! Compute reachable nodes assuming limited moves of the agents.
    //!
    //! An agent can only move for the first n time points, where n is the
    //! length of its shortest path from start to goal plus the given delta.
    //! Atoms reach(A,U,T) will be added indicating that an agent A can reach a
    //! node U at time point T.
    bool compute_reach(Clingo::Backend &bck, int delta) {
        if (!compute_sp(bck)) {
            return false;
        }
        for (auto *a : agents_) {
            if (!compute_forward_reach_(a, delta)) {
                return false;
            }
            compute_backward_reach_(a, delta);
            // add possible locations
            for (auto *node : nodes_) {
                for (int t = node->cost; t <= node->max_cost; ++t) {
                    auto atm = bck.add_atom(Clingo::Function("reach", {a->name, node->name, Clingo::Number(t)}));
                    bck.rule(false, {atm}, {});
                }
            }
        }
        return true;
    }
private:
    //! Compute the shortest path for a single agent.
    bool compute_sp_(Agent *a) {
        // ensure that the instance is sane enough to start computation
        if (a->start == nullptr || a->goal == nullptr) {
            return false;
        }
        for (auto *node : nodes_) {
            node->cost = std::numeric_limits<int>::max();
        }
        // a poor man's heap (clingo-dl has a proper one)
        std::set<Node*, CostNodeCmp> todo;
        a->start->cost = 0;
        todo.emplace(a->start);
        while (!todo.empty()) {
            auto *cur = *todo.begin();
            todo.erase(todo.begin());
            for (auto &out : cur->out) {
                if (cur->cost + 1 < out->cost) {
                    todo.erase(out);
                    out->cost = cur->cost + 1;
                    todo.emplace(out);
                }
            }
        }
        if (a->goal->cost == std::numeric_limits<int>::max()) {
            return false;
        }
        a->sp_len = Clingo::Number(static_cast<int>(a->goal->cost));
        return true;
    }

    //! Compute nodes reachable from the start postion of the agent.
    //!
    //! Returns false if the agent's goal cannot be reached and assumes that
    //! shortest paths have already been computed.
    bool compute_forward_reach_(Agent *a, int delta) {
        auto horizon = a->sp_len.number() + delta;
        // reset costs
        for (auto *node : nodes_) {
            node->cost = std::numeric_limits<int>::max();
            node->max_cost = std::numeric_limits<int>::min();
        }
        // compute blocked
        for (auto *b : agents_) {
            if (a != b) {
                b->goal->block = b->sp_len.number() + delta;
            }
            else {
                b->goal->block = std::numeric_limits<int>::max();
            }
        }
        // compute forward reachable nodes (via shortest path)
        {
            std::set<Node*, CostNodeCmp> todo;
            a->start->cost = 0;
            todo.emplace(a->start);
            while (!todo.empty()) {
                auto *cur = *todo.begin();
                todo.erase(todo.begin());
                // we cannot continue from this node anymore
                if (cur->cost >= horizon) {
                    continue;
                }
                for (auto &out : cur->out) {
                    // enter the node with the next larger cost if it is not blocked already
                    if (cur->cost + 1 < out->cost && cur->cost + 1 < out->block) {
                        todo.erase(out);
                        out->cost = cur->cost + 1;
                        todo.emplace(out);
                    }
                }
            }
            // we could not reach the goal node
            if (a->goal->cost == std::numeric_limits<int>::max()) {
                return false;
            }
        }
        return true;
    }

    //! Compute nodes reachable from the goal.
    //!
    //! This assumes a preceding call to compute_forward_reach_ for the same agent.
    void compute_backward_reach_(Agent *a, int delta) { // NOLINT(readability-convert-member-functions-to-static)
        auto horizon = a->sp_len.number() + delta;
        std::set<Node*, MaxCostNodeCmp> todo;
        // the goal has to be reached on the horizon
        a->goal->max_cost = horizon;
        todo.emplace(a->goal);
        while (!todo.empty()) {
            auto *cur = *todo.begin();
            todo.erase(todo.begin());
            // we cannot reach the start node anymore
            if (cur->cost > cur->max_cost) {
                continue;
            }
            for (auto &in : cur->in) {
                // incoming nodes are reached one time step earlier
                int c = 1;
                // except if they are blocked earlier
                if (cur->max_cost + 1 > in->block) {
                    // in [is not reachable at block anymore] --> cur [is reachable at cur->max_cost]
                    // this means that we want to set
                    //   in->max_cost = in->block - 1
                    c = cur->max_cost - in->block + 1;
                }
                if (cur->max_cost - c > in->max_cost) {
                    todo.erase(in);
                    in->max_cost = cur->max_cost - c;
                    todo.emplace(in);
                }
            }
        }
    }

    //! Mapping from node names to actual nodes.
    std::unordered_map<Clingo::Symbol, Node> node_map_;
    //! The list of nodes in insertion order.
    std::vector<Node*> nodes_;
    //! Mapping from agent names to actual agents.
    std::unordered_map<Clingo::Symbol, Agent> agent_map_;
    //! The list of agents in insertion order.
    std::vector<Agent*> agents_;
};

}

using Clingo::Detail::handle_error;

extern "C" void cmapf_version(int *major, int *minor, int *patch) {
    if (major != nullptr) {
        *major = CMAPF_VERSION_MAJOR;
    }
    if (minor != nullptr) {
        *minor = CMAPF_VERSION_MINOR;
    }
    if (patch != nullptr) {
        *patch = CMAPF_VERSION_REVISION;
    }
}

extern "C" bool cmapf_compute_min_delta(clingo_control_t *c_ctl, bool *res, int *delta) {
    CMAPF_TRY {
        auto ctl = Clingo::Control{c_ctl, false};
        MAPF prob;
        prob.init(ctl);
        auto ret = prob.compute_min_delta();
        if (ret.has_value()) {
            *res = true;
            *delta = ret.value();
        }
        else {
            *res = false;
            *delta = 0;
        }
    }
    CMAPF_CATCH;
}

extern "C" bool cmapf_compute_sp_length(clingo_control_t *c_ctl, bool *res) {
    CMAPF_TRY {
        auto ctl = Clingo::Control{c_ctl, false};
        MAPF prob;
        prob.init(ctl);
        ctl.with_backend([&prob, res](Clingo::Backend &bck) {
            *res = prob.compute_sp(bck);
        });
    }
    CMAPF_CATCH;
}

extern "C" bool cmapf_compute_reachable(clingo_control_t *c_ctl, int delta, bool *res) {
    CMAPF_TRY {
        auto ctl = Clingo::Control{c_ctl, false};
        MAPF prob;
        prob.init(ctl);
        ctl.with_backend([&prob, delta, res](Clingo::Backend &bck) {
            *res = prob.compute_reach(bck, delta);
        });
    }
    CMAPF_CATCH;
}
