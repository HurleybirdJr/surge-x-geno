import surgepy


def osc_param_values(surge_inst: surgepy.SurgeSynthesizer, current_patch: dict, osc_num: int):
    # Prints all osc paramters before "p" slider values
    print(param_values(surge_inst, current_patch["scene"][0]["osc"][osc_num]["type"]),
          param_values(surge_inst, current_patch["scene"][0]["osc"][osc_num]["pitch"]),
          param_values(surge_inst, current_patch["scene"][0]["osc"][osc_num]["octave"]),
          param_values(surge_inst, current_patch["scene"][0]["osc"][osc_num]["keytrack"]),
          param_values(surge_inst, current_patch["scene"][0]["osc"][osc_num]["retrigger"]),
          sep='\n'
          )
    for i in range(0, 7):  # Print all "p" parameters and values derived from osc type
        osc_params = current_patch["scene"][0]["osc"][osc_num]["p"][i]
        print(param_values(surge_inst, osc_params))


def param_values(surge_inst: surgepy.SurgeSynthesizer, param: surgepy.SurgeNamedParamId):
    return [
        surge_inst.getParameterName(param.getId()),
        surge_inst.getParamVal(param),
        surge_inst.getParamMin(param),
        surge_inst.getParamMax(param),
        surge_inst.getParamDef(param),
        surge_inst.getParamValType(param),
        surge_inst.getParamDisplay(param)
    ]


def refresh_patch(surge_inst: surgepy.SurgeSynthesizer, path: str):
    surge_inst.savePatch(path=path)
    surge_inst.loadPatch(path=path)


SURGE_INST = surgepy.createSurge(48000)
patch = SURGE_INST.getPatch()
# SURGE_INST.setParamVal(patch["scene"][0]["osc"][0]["type"], 8)
refresh_patch(SURGE_INST, "../patches/text.fxp")

osc_type: surgepy.SurgeNamedParamId = patch["scene"][0]["osc"][0]["type"]
osc_param_1 = patch["scene"][0]["osc"][0]
print(osc_param_values(SURGE_INST, patch, 0))
