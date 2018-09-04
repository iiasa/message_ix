tar cvzf db.tar.gz db
scp db.tar.gz $1:/opt/data.ene.iiasa.ac.at/docs/continuous_integration/scenario_db/
rm db.tar.gz
