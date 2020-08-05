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

utils::globalVariables(c("ixmp_path"))

.onLoad <- function(libname, pkgname) {

  ## Set path ixmp folder in message_ix working copy
  ixmp_path <<- Sys.getenv("IXMP_PATH")

  if(ixmp_path == "")
    warning("Check MESSAGE model installation")
  
  # careful to have all the slashes in the same direction
  model_file = gsub("/","\\\\" ,file.path( paste(ixmp_path, "\\message_ix\\model", sep = '') , "{model}_run.gms" ) )
  inp = gsub("/","\\\\" , file.path( paste(ixmp_path, "\\message_ix\\model\\data", sep = '') , "MsgData_{case}.gdx" ) )
  outp = gsub("/","\\\\" , file.path( paste(ixmp_path, "\\message_ix\\model\\output", sep = '') , "MsgOutput_{case}.gdx" ) )
  iter_file = gsub("/","\\\\" , file.path( paste(ixmp_path, "\\message_ix\\model\\output", sep = '') , "MsgIterationReport_{case}.gdx" ) )
  solve_args = paste("--in=",inp," --out=",outp," --iter=", iter_file, sep = '')
  
  for (i in c("MESSAGE","MESSAGE-MACRO")) {
    ModelConfig[[i]] <<- list(model_file = model_file,
                             inp = inp,
                             outp = outp,
                             args = solve_args)
  }

}
