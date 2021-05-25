# NB this file is preserved from the removed 'rmessageix' package, to perhaps
#    be integrated into the pytest suite

test_that('message_ix.Scenario can be instantiated', {
  mp <- ixmp$Platform(backend = "jdbc", driver = "hsqldb",
                      url="jdbc:hsqldb:mem:rmessageix test")
  scen <- message_ix$Scenario(mp, "model name", "scenario name",
                              version = "new")
})
