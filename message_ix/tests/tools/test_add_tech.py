from message_ix.testing import make_dantzig
from message_ix.tools.add_tech import print_df


def test_print_df(test_mp, request, test_data_path, tmp_path):
    scen = make_dantzig(test_mp, quiet=True, request=request)
    scen.check_out()
    path = test_data_path.joinpath("add_tech")
    output_dir = tmp_path.joinpath("add_tec")
    output_dir.mkdir()
    print_df(
        scenario=scen,
        input_path=str(path.joinpath("westeros_carbon_removal_data.yaml")),
        output_dir=output_dir,
    )

    # TODO: adapt this to read parameter names from yaml file
    parameter_list = scen.par_list()
    for parameter in parameter_list:
        assert (output_dir / f"{parameter}.xlsx").exists()


# def test_get_values():
#     get_values()


# def test_get_report():
#     get_report()
