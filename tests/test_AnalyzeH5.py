import subprocess
import os
import shutil

def test_run_analyzeh5_and_compare():

    # Delete existing 'test' directory if it exists and make new one
    if os.path.exists('test'):
        shutil.rmtree('test')
    os.makedirs('test')

    result = subprocess.run(["python", "../scripts/AnalyzeH5.py", "-f", "testData/lowFlux/SimpleClusters_c0_r334_n100.h5", "-p", "test", "-r", "666", "-s", "2,15", "-sb", "-a", "1"])

    #print(result.stdout)
    #print(result.stderr)

    # List of file pairs
    file_pairs = [
        ("test/AnalyzeH5_r666_c0_r1_c14_testLabel_E.png", "testData/expected/analyzeH5Expected/AnalyzeH5_r666_c0_r1_c14_testLabel_E.png"),
        ("test/AnalyzeH5_r666_c0_testLabel_E.png", "testData/expected/analyzeH5Expected/AnalyzeH5_r666_c0_testLabel_E.png"),
        ("test/AnalyzeH5_r666_c0_testLabel_gainDistribution.png", "testData/expected/analyzeH5Expected/AnalyzeH5_r666_c0_testLabel_gainDistribution.png"),
        ("test/AnalyzeH5_r666_c0_r1_c14_testLabel_fitInfo.npy", "testData/expected/analyzeH5Expected/AnalyzeH5_r666_c0_r1_c14_testLabel_fitInfo.npy")
    ]

    for file1, file2 in file_pairs:
        diff_result = subprocess.run(["diff", file1, file2])
        assert diff_result.returncode == 0
