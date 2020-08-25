#' message_ix-R core
#'
#' This package provides MESSAGE-ix model specifications to the ix modeling platform (ixmp).
#'
#' @name rmessageix
NULL

#' @import reticulate
NULL

.onAttach = function(libname, pkgname){
  packageStartupMessage(
    sprintf("Loaded rmessageix v%s. See ?rmessageix for help",
            utils::packageDescription(pkgname)$Version) )
}

.onLoad <- function(libname, pkgname) {
  # Make ixmp and message_ix available in the global namespace
  assign("ixmp", reticulate::import("ixmp", delay_load = TRUE), .GlobalEnv)
  assign("message_ix", reticulate::import("message_ix", delay_load = TRUE),
         .GlobalEnv)
}
