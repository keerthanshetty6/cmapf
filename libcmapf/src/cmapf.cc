#include <sstream>
#include <set>
#include <optional>
#include <limits>

#include <clingo.hh>

#include "cmapf.h"

#define CMAPF_TRY try // NOLINT
#define CMAPF_CATCH catch (...){ Clingo::Detail::handle_cxx_error(); return false; } return true // NOLINT

namespace {

struct Graph {
    struct Node {
        Node(Clingo::Symbol sym) : sym{sym} { }

        Clingo::Symbol sym;
        std::vector<Node*> out;
        std::vector<Node*> in;
        Node *prev = nullptr;
        int cost = std::numeric_limits<int>::max();
        int max_cost = 0;
        int block = std::numeric_limits<int>::max();

    };
    struct CostNodeCmp {
        bool operator()(Node *a, Node *b) const {
            return a->cost < b->cost;
        }
    };
    struct MaxCostNodeCmp {
        bool operator()(Node *a, Node *b) const {
            return a->max_cost > b->max_cost;
        }
    };
    struct Agent {
        Agent(Clingo::Symbol sym) : sym{sym} { }
        void check() const {
            if (start == nullptr || goal == nullptr) {
                throw std::runtime_error("agent with invalid start and goal");
            }
        }
        Clingo::Symbol sym;
        Node *start = nullptr;
        Node *goal = nullptr;
        Clingo::Symbol sp = Clingo::Supremum();
    };
    Node *add_node(Clingo::Symbol u) {
        return &nodes.try_emplace(u, u).first->second;
    }
    Agent *add_agent(Clingo::Symbol a) {
        auto ins = agent_map_.try_emplace(a, a);
        if (ins.second) {
            agents_.emplace_back(&ins.first->second);
        }
        return &ins.first->second;
    }
    void add_start(Clingo::Symbol a, Clingo::Symbol u) {
        add_agent(a)->start = add_node(u);
    }
    void add_goal(Clingo::Symbol a, Clingo::Symbol u) {
        add_agent(a)->goal = add_node(u);
    }
    void add_edge(Clingo::Symbol u, Clingo::Symbol v) {
        auto *n_u = add_node(u);
        auto *n_v = add_node(v);
        n_u->out.emplace_back(n_v);
        n_v->in.emplace_back(n_u);
    }
    void compute_sp(Clingo::Backend &bck) {
        for (auto *a : agents_) {
            a->check();
            for (auto &[name, node] : nodes) {
                node.cost = std::numeric_limits<int>::max();
                node.prev = nullptr;
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
                        out->prev = cur;
                        out->cost = cur->cost + 1;
                        todo.emplace(out);
                    }
                }
            }
            if (a->goal->cost != std::numeric_limits<int>::max()) {
                a->sp = Clingo::Number(static_cast<int>(a->goal->cost));
            }
            auto atm = bck.add_atom(Clingo::Function("shortest_path", {a->sym, a->sp}));
            bck.rule(false, {atm}, {});
        }
    }
    void compute_reach(Clingo::Backend &bck, int delta) {
        // there are no reachable positions if the goal is not reachable
        for (auto *a : agents_) {
            if (a->sp.type() != Clingo::SymbolType::Number) {
                return;
            }
        }
        for (auto *a : agents_) {
            auto horizon = a->sp.number() + delta;
            for (auto &[name, node] : nodes) {
                node.cost = std::numeric_limits<int>::max();
                node.max_cost = std::numeric_limits<int>::min();
                node.prev = nullptr;
            }
            // compute blocked
            for (auto *b : agents_) {
                if (a != b) {
                    b->goal->block = b->sp.number() + delta;
                }
                else {
                    b->goal->block = std::numeric_limits<int>::max();
                }
            }
            // compute forward reachable nodes (via shortest path)
            // TODO: stop early if cost above horizon
            {
                std::set<Node*, CostNodeCmp> todo;
                a->start->cost = 0;
                todo.emplace(a->start);
                while (!todo.empty()) {
                    auto *cur = *todo.begin();
                    todo.erase(todo.begin());
                    for (auto &out : cur->out) {
                        if (cur->cost + 1 < out->cost && cur->cost + 1 < out->block) {
                            todo.erase(out);
                            out->prev = cur;
                            out->cost = cur->cost + 1;
                            todo.emplace(out);
                        }
                    }
                }
            }
            // compute backward reachable nodes on transpose
            // TODO: stop early if max_cost drops below cost
            {
                std::set<Node*, MaxCostNodeCmp> todo_max;
                a->goal->max_cost = horizon;
                todo_max.emplace(a->goal);
                while (!todo_max.empty()) {
                    auto *cur = *todo_max.begin();
                    todo_max.erase(todo_max.begin());
                    for (auto &in : cur->in) {
                        int c = 1;
                        if (cur->max_cost + 1 > in->block) {
                            // [not reachable at block anymore] in --> cur [reachable at cur->max_cost]
                            // this means that we want to set
                            //   in->max_cost = in->block - 1
                            c = cur->max_cost - in->block + 1;
                        }
                        if (cur->max_cost - c > in->max_cost) {
                            todo_max.erase(in);
                            in->max_cost = cur->max_cost - c;
                            todo_max.emplace(in);
                        }
                    }
                }
            }
            // add possible locations
            for (auto &[name, node] : nodes) {
                if (node.prev == nullptr && &node != a->start) {
                    continue;
                }
                for (int t = node.cost; t <= node.max_cost; ++t) {
                    auto atm = bck.add_atom(Clingo::Function("reach", {a->sym, node.sym, Clingo::Number(t)}));
                    bck.rule(false, {atm}, {});
                }
            }
        }
    }

    std::unordered_map<Clingo::Symbol, Node> nodes;
    std::unordered_map<Clingo::Symbol, Agent> agent_map_;
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
        Graph g;
        auto syms = ctl.symbolic_atoms();
        for (auto it = syms.begin(Clingo::Signature{"start", 2}), ie = syms.end(); it != ie; ++it) {
            auto args = it->symbol().arguments();
            g.add_start(args.front(), args.back());
        }
        for (auto it = syms.begin(Clingo::Signature{"goal", 2}), ie = syms.end(); it != ie; ++it) {
            auto args = it->symbol().arguments();
            g.add_goal(args.front(), args.back());
        }
        for (auto it = syms.begin(Clingo::Signature{"edge", 2}), ie = syms.end(); it != ie; ++it) {
            auto args = it->symbol().arguments();
            g.add_edge(args.front(), args.back());
        }
        ctl.with_backend([&g, delta](Clingo::Backend &bck) {
            g.compute_sp(bck);
            g.compute_reach(bck, delta);
        });
    }
    CMAPF_CATCH;
}
