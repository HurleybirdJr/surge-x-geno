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

# TODO:
#       Bind release time to extend audio file duration from hold length
#       Decide on maximum release time for training data (4 secs?)


MAX_PATCHES = 10000

OSC_ACC_FAC = [1, 2, 4, 5, 8, 10, 20, 25, 40, 50, 100, 200]
OSC_ACC: int = 25  # OSC parameter value % increment - MUST MATCH FACTORS
WIDTH_ACC_FAC = [1, 2, 4, 5, 10, 20, 25, 50, 100]
WIDTH_ACC: int = 10  # Width Parameter % increment - MUST MATCH FACTORS

SAMPLE_RATE = 48000

# MIDI Setup
NOTE = 36  # C2
DURATION = 2  # Note length in seconds (+ release time?)
VELOCITY = 100  # MIDI velocity


#  Refreshes current patch data - parameter values won't update unless I do this shiz :/
def refresh_patch(surge_inst: surgepy.SurgeSynthesizer, path: str):
    surge_inst.savePatch(path=path)
    surge_inst.loadPatch(path=path)


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


SURGE_INST = surgepy.createSurge(SAMPLE_RATE)  # Initialises SurgeXT instance

# Set parameter values
patch = SURGE_INST.getPatch()

# PATCH SETUP HERE
SURGE_INST.setParamVal(patch["scene"][0]["osc"][0]["type"], 8)  # Set OSC Type HERE!!
refresh_patch(SURGE_INST, "../patches/temp.fxp")


#  Export and render .wav files
def render(sptwnhv):
    saw, pulse, tri, width, note, hold, velocity = sptwnhv

    SURGE_INST.setParamVal(patch["scene"][0]["osc"][0]["p"][0], saw)  # SAW
    SURGE_INST.setParamVal(patch["scene"][0]["osc"][0]["p"][1], pulse)  # PULSE
    SURGE_INST.setParamVal(patch["scene"][0]["osc"][0]["p"][2], tri)  # TRIANGLE
    SURGE_INST.setParamVal(patch["scene"][0]["osc"][0]["p"][3], width)  # PULSE WIDTH

    one_sec = 2 * SURGE_INST.getSampleRate() / SURGE_INST.getBlockSize()
    length = int(round(DURATION * one_sec))
    buffer = SURGE_INST.createMultiBlock(length)
    intermission = int(round((DURATION - hold) * one_sec))

    # for note in chd:
    SURGE_INST.playNote(0, note, velocity, 0)
    SURGE_INST.processMultiBlock(buffer, 0, intermission)

    # for note in chd:
    SURGE_INST.releaseNote(0, note, 0)
    SURGE_INST.processMultiBlock(buffer, intermission, length - intermission)

    buffer = (buffer * (2 ** 15 - 1)).astype("<h")  # Convert to little-endian 16 bit int.
    # WHY? float round
    with wave.open(f"../output/rng/{saw}_{pulse}_{tri}_{width}.wav", "w") as file:
        file.setnchannels(1)  # 2 channels
        file.setsampwidth(2)
        file.setframerate(SAMPLE_RATE)
        file.writeframes(buffer[0].tobytes())


#  Creates MIDI notes to play with current SurgeXT patch
def generate_random_patch_parameter_values():
    for count in range(MAX_PATCHES):
        saw_val, pulse_val, tri_val, pw_val = (
            random.uniform(-1, 1),
            random.uniform(-1, 1),
            random.uniform(-1, 1),
            random.uniform(0, 1)
        )
        yield saw_val, pulse_val, tri_val, pw_val, NOTE, (DURATION // 2), VELOCITY


# Multithread processing - YIPPEE! (probably could be done differently IDK?)
core_num = multiprocessing.cpu_count()
print(f"{core_num} cores")

process_pool = multiprocessing.Pool(core_num // 2)
r = list(tqdm(process_pool.imap(render, generate_random_patch_parameter_values()), total=MAX_PATCHES))

# Check if ACCURACY values are valid factors
# if (OSC_ACC in OSC_ACC_FAC) and (WIDTH_ACC in WIDTH_ACC_FAC):
#     print("GOOD!")
#     osc_inc: int = (100 // OSC_ACC) + 1
#     width_inc: int = (50 // WIDTH_ACC) + 1
#
#     for sawtooth in range(0, osc_inc):
#         print(f"SAW {OSC_ACC * sawtooth}%")
#
#     for triangle in range(0, osc_inc):
#         print(f"TRI {OSC_ACC * triangle}%")
#
#     for square in range(0, osc_inc):
#         for width in range(0, width_inc):
#             print(f"SQR {OSC_ACC * square}% - WIDTH {WIDTH_ACC * width}%")

# render([40, DURATION / 2, 100])
