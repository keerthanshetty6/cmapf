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
struct MAPF {
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
            return u->cost < v->cost;
        }
    };
    //! Sort nodes in descending order according to their maximum cost.
    struct MaxCostNodeCmp {
        bool operator()(Node *u, Node *v) const {
            return u->max_cost > v->max_cost;
        }
    };
    //! An agent in a MAPF problem.
    struct Agent {
        Agent(Clingo::Symbol name) : name{name} { }
        void check() const {
            if (start == nullptr || goal == nullptr) {
                throw std::runtime_error("agent with invalid start and goal");
            }
        }
        Clingo::Symbol name;
        Node *start = nullptr;
        Node *goal = nullptr;
        Clingo::Symbol sp_len = Clingo::Supremum();
    };
    //! Add a node with the given name to the MAPF problem.
    //!
    //! Returns the same node for the same name.
    Node *add_node(Clingo::Symbol u) {
        return &nodes.try_emplace(u, u).first->second;
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
    //! Compute the length of the shortest paths between start and goal nodes
    //! of agents.
    //!
    //! A corresponding atom shortest_path(A,L) is added to the given backend
    //! indicating that agent A can reach its goal within L time steps.
    //! Furthermore, the shortest path is stored for later use along with the
    //! agents.
    void compute_sp(Clingo::Backend &bck) {
        for (auto *a : agents_) {
            a->check();
            for (auto &[name, node] : nodes) {
                node.cost = std::numeric_limits<int>::max();
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
            if (a->goal->cost != std::numeric_limits<int>::max()) {
                a->sp_len = Clingo::Number(static_cast<int>(a->goal->cost));
            }
            auto atm = bck.add_atom(Clingo::Function("shortest_path", {a->name, a->sp_len}));
            bck.rule(false, {atm}, {});
        }
    }
    //! Compute reachable nodes assuming limited moves of the agents.
    //!
    //! An agent can only move for the first n time points, where n is the
    //! length of its shortest path from start to goal plus the given delta.
    //! Atoms reach(A,U,T) will be added indicating that an agent A can reach a
    //! node U at time point T.
    void compute_reach(Clingo::Backend &bck, int delta) {
        // do not compute reachable positions if one agent cannot reach its goal
        for (auto *a : agents_) {
            if (a->sp_len.type() != Clingo::SymbolType::Number) {
                return;
            }
        }
        for (auto *a : agents_) {
            auto horizon = a->sp_len.number() + delta;
            for (auto &[name, node] : nodes) {
                node.cost = std::numeric_limits<int>::max();
                node.max_cost = std::numeric_limits<int>::min();
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
            }
            // compute backward reachable nodes on transpose
            {
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
            // add possible locations
            for (auto &[name, node] : nodes) {
                for (int t = node.cost; t <= node.max_cost; ++t) {
                    auto atm = bck.add_atom(Clingo::Function("reach", {a->name, node.name, Clingo::Number(t)}));
                    bck.rule(false, {atm}, {});
                }
            }
        }
    }

    //! Mapping from node names to actual nodes.
    std::unordered_map<Clingo::Symbol, Node> nodes;
    //! Mapping from agent names to actual agents.
    std::unordered_map<Clingo::Symbol, Agent> agent_map_;
    //! The list of agents in the MAPF problem in insertion order.
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

extern "C" bool cmapf_compute_reachable(clingo_control_t *c_ctl, int delta) {
    CMAPF_TRY {
        auto ctl = Clingo::Control{c_ctl, false};
        MAPF prob;
        auto syms = ctl.symbolic_atoms();
        for (auto it = syms.begin(Clingo::Signature{"start", 2}), ie = syms.end(); it != ie; ++it) {
            auto args = it->symbol().arguments();
            prob.add_start(args.front(), args.back());
        }
        for (auto it = syms.begin(Clingo::Signature{"goal", 2}), ie = syms.end(); it != ie; ++it) {
            auto args = it->symbol().arguments();
            prob.add_goal(args.front(), args.back());
        }
        for (auto it = syms.begin(Clingo::Signature{"edge", 2}), ie = syms.end(); it != ie; ++it) {
            auto args = it->symbol().arguments();
            prob.add_edge(args.front(), args.back());
        }
        ctl.with_backend([&prob, delta](Clingo::Backend &bck) {
            prob.compute_sp(bck);
            prob.compute_reach(bck, delta);
        });
    }
    CMAPF_CATCH;
}
