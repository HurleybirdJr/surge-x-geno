import surgepy
import sys
import wave
import os
import random
import multiprocessing
from tqdm.auto import tqdm


def param_values(surge_inst, param):
    return [
        surge_inst.getParamVal(param),
        surge_inst.getParamMin(param),
        surge_inst.getParamMax(param),
        surge_inst.getParamDef(param),
        surge_inst.getParamValType(param),
        surge_inst.getParamDisplay(param),
        surge_inst.getParameterName(param.getId())
    ]


MAX_PATCHES = 1
SAMPLE_RATE = 48000

# Typical piano note range
NOTE_RANGE = [21, 108]
DURATION = 4  # seconds
MAX_VELOCITY = 127

SURGE_INST = surgepy.createSurge(SAMPLE_RATE)

# Set param values
patch = SURGE_INST.getPatch()
SURGE_INST.setParamVal(patch["scene"][0]["osc"][0]["type"], 8)
SURGE_INST.savePatch(path="patches/text.fxp")
SURGE_INST.loadPatch(path="patches/text.fxp")
# SURGE_INST.setParamVal(patch["scene"][0]["osc"][0]["p"][2], 1)

osc_type: surgepy.SurgeNamedParamId = patch["scene"][0]["osc"][0]["type"]
osc_param_1 = patch["scene"][0]["osc"][0]
print(param_values(SURGE_INST, osc_type))
for i in range(0, 7):
    osc_params = patch["scene"][0]["osc"][0]["p"][i]
    print(param_values(SURGE_INST, osc_params))


def render(nhv):
    note, hold, velocity = nhv

    onesec = SURGE_INST.getSampleRate() / SURGE_INST.getBlockSize()
    buffer = SURGE_INST.createMultiBlock(int(round(DURATION * onesec)))

    chd = [note]
    for note in chd:
        SURGE_INST.playNote(0, note, velocity, 0)
    SURGE_INST.processMultiBlock(buffer, 0, int(round(hold * onesec)))

    for note in chd:
        SURGE_INST.releaseNote(0, note, 0)
    SURGE_INST.processMultiBlock(buffer, int(round((DURATION - hold) * onesec)))

    # slug, buf.T, int(round(SURGE_INST.getSampleRate())))

    buffer = (buffer * (2 ** 15 - 1)).astype("<h")  # Convert to little-endian 16 bit int.
    # WHY? float round
    with wave.open("output/note%d_velocity%d_hold%f.wav" % (note, velocity, hold), "w") as file:
        file.setnchannels(2)  # 2 channels
        file.setsampwidth(2)
        file.setframerate(SAMPLE_RATE)
        file.writeframes(buffer.tobytes())


def generate_patch_note_hold_and_velocity():
    for i in range(MAX_PATCHES):
        for note in range(NOTE_RANGE[0], NOTE_RANGE[1]):
            hold = 1
            velocity = random.randint(1, MAX_VELOCITY)
            yield note, hold, velocity


core_num = multiprocessing.cpu_count()
print(f"{core_num} cores")

process_pool = multiprocessing.Pool(core_num // 2)
r = list(tqdm(process_pool.imap(render, generate_patch_note_hold_and_velocity()), total=MAX_PATCHES))
