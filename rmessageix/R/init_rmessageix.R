#' message_ix-R core
#'
#' This package provides MESSAGE-ix model specifications to the ix modeling platform (ixmp).
#'
#' @name rmessageix
NULL

#' @import rixmp
NULL

.onAttach = function(libname, pkgname){
  packageStartupMessage(
    sprintf("Loaded rmessageix v%s. See ?rmessageix for help",
            utils::packageDescription(pkgname)$Version) )
}

message_ix <- NULL

.onLoad <- function(libname, pkgname) {
  # Set message_ix in the global namespace
  message_ix <<- reticulate::import("message_ix", delay_load = TRUE)
}
