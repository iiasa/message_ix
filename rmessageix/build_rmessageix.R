#Build a developed R package to binary and display help

require(devtools)

# set in Github/local folder
rmessageix_path=paste0(getwd(),"/rmessageix/")
setwd(paste0(rmessageix_path,"/source/"))

# Build binary
devtools::build(pkg = ".", path=rmessageix_path,binary=T)

# install the package from binary
setwd(rmessageix_path)
install.packages("rmessageix_0.0.0.9000.zip", repos=NULL)

pkg = "rmessageix"
setwd(paste0(rmessageix_path,"/source/"))

static_help = function(pkg, links = tools::findHTMLlinks()) {
  pkgRdDB = tools:::fetchRdDB(file.path(find.package(pkg), 'help', pkg))
  force(links); topics = names(pkgRdDB)
  for (p in topics) {
    tools::Rd2HTML(pkgRdDB[[p]], paste("./inst/docum/",p, '.html', sep = ''),
                   package = pkg, Links = links, no_links = is.null(links))
  }
}

static_help(pkg,links = tools::findHTMLlinks())
print("Documentation created!!")
