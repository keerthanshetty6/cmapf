#ifndef CMAPF_H
#define CMAPF_H

//! Major version number.
#define CMAPF_VERSION_MAJOR 1
//! Minor version number.
#define CMAPF_VERSION_MINOR 0
//! Revision number.
#define CMAPF_VERSION_REVISION 0
//! String representation of version.
#define CMAPF_VERSION "1.0.0"

#ifdef __cplusplus
extern "C" {
#endif

#if defined _WIN32 || defined __CYGWIN__
#   define CMAPF_WIN
#endif
#ifdef CMAPF_NO_VISIBILITY
#   define CMAPF_VISIBILITY_DEFAULT
#   define CMAPF_VISIBILITY_PRIVATE
#else
#   ifdef CMAPF_WIN
#       ifdef CMAPF_BUILD_LIBRARY
#           define CMAPF_VISIBILITY_DEFAULT __declspec (dllexport)
#       else
#           define CMAPF_VISIBILITY_DEFAULT __declspec (dllimport)
#       endif
#       define CMAPF_VISIBILITY_PRIVATE
#   else
#       if __GNUC__ >= 4
#           define CMAPF_VISIBILITY_DEFAULT  __attribute__ ((visibility ("default")))
#           define CMAPF_VISIBILITY_PRIVATE __attribute__ ((visibility ("hidden")))
#       else
#           define CMAPF_VISIBILITY_DEFAULT
#           define CMAPF_VISIBILITY_PRIVATE
#       endif
#   endif
#endif

#include <clingo.h>

// NOLINTBEGIN(modernize-use-trailing-return-type,modernize-use-using)

//! Configure for which objective to compute reachable positions.
enum cmapf_objective {
    cmapf_objective_sum_of_costs = 0, //!< The sum of costs objective.
    cmapf_objective_makespan = 1     //!< The makespan objective.
};
//! Corresponds to reachable_type.
typedef int cmapf_objective_t;

typedef struct cmapf_problem cmapf_problem_t;

//! Obtain the version of the library.
CMAPF_VISIBILITY_DEFAULT void cmapf_version(int *major, int *minor, int *patch);

//! Create a MAPF problem instance initializing it from the facts in the given control object.
//!
//! Facts over start/2, goal/2, and edge/2 are used for initialization.
CMAPF_VISIBILITY_DEFAULT bool cmapf_problem_construct(cmapf_problem_t **problem, clingo_control_t *c_ctl);

//! Destroy the given MAPF problem instance.
CMAPF_VISIBILITY_DEFAULT void cmapf_problem_destroy(cmapf_problem_t *problem);

//! Compute the minimal delta or horizon for which the given MAPF problem is
//! not trivially unsatisfiable.
//!
//! For the sum of costs objective this is a delta value and for the makespan
//! objective this is a horizon.
//!
//! If the MAPF problem is detected to be unsatisfiable sets res to false.
CMAPF_VISIBILITY_DEFAULT bool cmapf_problem_min_delta_or_horizon(cmapf_problem_t *problem, cmapf_objective_t type, bool *res, int *delta);

//! Compute the shortest path length from start to goal for each agent.
//!
//! The function terminates early and sets the result to false if there is no
//! shortest path for some agent.
//!
//! Atoms over predicate sp_length/2 are added to the problem. Atom
//! sp_length(A,L) indicates that agent A can reach its goal within L time
//! steps from its start ignoring any collisions with other agents.
CMAPF_VISIBILITY_DEFAULT bool cmapf_problem_add_sp_length(cmapf_problem_t *problem, clingo_control_t *c_ctl, bool *res);

//! Compute an approximation of reachable nodes assuming limited moves of the
//! agents.
//!
//! The function terminates early and sets the result to false if there is an
//! agent that cannot reach its goal.
//!
//! For the sum of costs objective, an agent can only move for the first n time
//! points, where n is the length of its shortest path from start to goal plus
//! the given delta.
//!
//! For the makespan objective, an agent can move during the given horizon.
//!
//! The function assumes that the control object already holds a MAPF problem
//! in standard form.
//!
//! Atoms over the predicates reach/3 and sp_length/2 are added to the control
//! object. Atoms reach(A,U,T) indicate that an agent A can reach a node U at
//! time point T. Atoms over predicate sp_length correspond to what is added
//! with cmapf_compute_reachable(). The shortest path length is only added for
//! the sum of costs objective.
CMAPF_VISIBILITY_DEFAULT bool cmapf_problem_add_reachable(cmapf_problem_t *problem, clingo_control_t *c_ctl, cmapf_objective_t type, int delta_or_horizon, bool *res);

//! Helper to count the atoms over the given signature.
CMAPF_VISIBILITY_DEFAULT bool cmapf_count_atoms(clingo_symbolic_atoms_t *c_syms, char const *name, int arity, int *res);

#ifdef __cplusplus
}
#endif

// NOLINTEND(modernize-use-trailing-return-type,modernize-use-using)

#endif
