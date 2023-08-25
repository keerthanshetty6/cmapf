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

//! Obtain the version of the library.
CMAPF_VISIBILITY_DEFAULT void cmapf_version(int *major, int *minor, int *patch);

//! Compute the minimal delta for which the MAPF problem in the control object
//! is not trivially unsatisfiable.
//!
//! If the MAPF problem is detected to be unsatisfiable sets res to false.
CMAPF_VISIBILITY_DEFAULT bool cmapf_compute_min_delta(clingo_control_t *c_ctl, bool *res, int *delta);

//! Compute the shortest path length from start to goal for each agent.
//!
//! The function terminates early and sets the result to false if there is no
//! shortest path for some agent.
//!
//! Atoms over predicate sp_length/2 are added to the problem. Atom
//! sp_length(A,L) indicates that agent A can reach its goal within L time
//! steps from its start ignoring any collisions with other agents.
CMAPF_VISIBILITY_DEFAULT bool cmapf_compute_sp_length(clingo_control_t *c_ctl, bool *res);

//! Compute an approximation of reachable nodes assuming limited moves of the
//! agents.
//!
//! The function terminates early and sets the result to false if there is an
//! agent that cannot reach its goal.
//!
//! An agent can only move for the first n time points, where n is the
//! length of its shortest path from start to goal plus the given delta.
//!
//! The function assumes that the control object already holds a MAPF problem
//! in standard form.
//!
//! Atoms over the predicates reach/3 and sp_length/2 are added to the control
//! object. Atoms reach(A,U,T) indicate that an agent A can reach a node U at
//! time point T. Atoms over predicate sp_length correspond to what is added
//! with cmapf_compute_reachable().
CMAPF_VISIBILITY_DEFAULT bool cmapf_compute_reachable(clingo_control_t *c_ctl, int delta, bool *res);

#ifdef __cplusplus
}
#endif

#endif
