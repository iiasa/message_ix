test_that('message_ix.Platform can be instantiated', {
  mp <- ixmp$Platform(backend = "jdbc", driver = "hsqldb",
                      url="jdbc:hsqldb:mem:rmessageix test")
  scen <- message_ix$Platform(mp, "model name", "scenario name")
})
