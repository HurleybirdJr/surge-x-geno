import surgepy
import wave
import random
import multiprocessing
from tqdm.auto import tqdm

'''
This code will hopefully both generate and export .wav
    and linked metadata files of various SurgeXT patch 
    parameter values and their outputs for the AI model 
    to learn from to hopefully replicate as closely as 
    possible based off of what SurgeXT can currently do.
    
    That's the plan anyways... (:
'''


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
DURATION = 1  # seconds
MAX_VELOCITY = 100  # MIDI velocity

SURGE_INST = surgepy.createSurge(SAMPLE_RATE)  # Initialises SurgeXT instance

# Set parameter values
patch = SURGE_INST.getPatch()

# PATCH SETUP HERE

SURGE_INST.setParamVal(patch["scene"][0]["osc"][0]["type"], 8)  # Set OSC Type HERE!!
SURGE_INST.setParamVal(patch["scene"][0]["osc"][0]["p"][0], 1.0)
SURGE_INST.setParamVal(patch["scene"][0]["osc"][0]["p"][1], 0.0)
SURGE_INST.setParamVal(patch["scene"][0]["osc"][0]["p"][2], 0.0)
SURGE_INST.setParamVal(patch["scene"][0]["osc"][0]["p"][3], 0.5)

# SURGE_INST.savePatch(path="../patches/temp.fxp")
SURGE_INST.loadPatch(path="../patches/Sine Fall 1 Sec.fxp")
# SURGE_INST.setParamVal(patch["scene"][0]["osc"][0]["p"][2], 1)

osc_type: surgepy.SurgeNamedParamId = patch["scene"][0]["osc"][0]["type"]
osc_param_1 = patch["scene"][0]["osc"][0]
print(param_values(SURGE_INST, osc_type))
for i in range(0, 7):
    osc_params = patch["scene"][0]["osc"][0]["p"][i]
    print(param_values(SURGE_INST, osc_params))

print(f"sample rate: {SURGE_INST.getSampleRate()}, block size: {SURGE_INST.getBlockSize()}")
print(f"one_sec: {(SURGE_INST.getSampleRate() / SURGE_INST.getBlockSize())} ")
print(f"buffer: {SURGE_INST.createMultiBlock(int(round(DURATION * (SURGE_INST.getSampleRate() / SURGE_INST.getBlockSize()))))}")
print(int(round((DURATION - 1) * (SURGE_INST.getSampleRate() / SURGE_INST.getBlockSize()))))


#  Export and render .wav files
def render(nhv):
    note, hold, velocity = nhv

    one_sec = 2 * SURGE_INST.getSampleRate() / SURGE_INST.getBlockSize()
    buffer = SURGE_INST.createMultiBlock(int(round(DURATION * one_sec)))

    chd = [note]
    for note in chd:
        SURGE_INST.playNote(0, note, velocity, 0)
    SURGE_INST.processMultiBlock(buffer, 0, int(round(DURATION * one_sec)))

    for note in chd:
        SURGE_INST.releaseNote(0, note, 0)
    SURGE_INST.processMultiBlock(buffer, int(round((DURATION - hold) * one_sec)))

    # slug, buf.T, int(round(SURGE_INST.getSampleRate())))

    buffer = (buffer * (2 ** 15 - 1)).astype("<h")  # Convert to little-endian 16 bit int.
    # WHY? float round
    with wave.open("../output/note%d_velocity%d_hold%f.wav" % (note, velocity, DURATION), "w") as file:
        file.setnchannels(1)  # 2 channels
        file.setsampwidth(2)
        file.setframerate(SAMPLE_RATE)
        file.writeframes(buffer[0].tobytes())


#  Creates MIDI notes to play with current SurgeXT patch
def generate_patch_note_hold_and_velocity():
    for count in range(MAX_PATCHES):
        for note in range(NOTE_RANGE[0], NOTE_RANGE[1]):
            hold = 1
            velocity = random.randint(1, MAX_VELOCITY)
            yield note, hold, velocity


# Multithread processing - YIPPEE! (probably could be done differently IDK?)
# core_num = multiprocessing.cpu_count()
# print(f"{core_num} cores")

# process_pool = multiprocessing.Pool(core_num // 2)
# r = list(tqdm(process_pool.imap(render, generate_patch_note_hold_and_velocity()), total=MAX_PATCHES))
render([40, DURATION / 2, 100])
