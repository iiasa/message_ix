import ixmp
import message_ix
import traceback
import yaml

with open("./scenarios.yaml", mode="r") as f:
    d = yaml.safe_load(f)

mp = ixmp.Platform("ixmp_dev")

for name, data in d.items():
    print("Testing", data["model"], data["scenario"])
    try:
        s = message_ix.Scenario(mp, data["model"], data["scenario"])
        scen = s.clone(
            scenario=data["scenario"] + "observing_current_obj_value",
            keep_solution=False,
        )
        scen.solve(model=data["solve"], solve_options=data["solve_options"])
        data["obs"] = scen.var("OBJ")["lvl"]
    except Exception as e:
        data["obs"] = "Failed with message: " + str(e)
        print(traceback.format_exc())

with open("./scenarios_obs.yaml", mode="w") as f:
    yaml.safe_dump(d, f)
