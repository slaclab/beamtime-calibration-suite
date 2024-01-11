# b4 running, make dir ../scan, and move scan_expected dir to ../scan_expected
# results in ../scan will get overridden each run, so no need to delete
python EventScanParallelSlice.py -r 349 > out.txt # output noisy so hide
python EventScanParallelSlice.py -r 349 -f ../scan/EventScanParallel_c0_r349_n1.h5 >> out.txt
if diff -r ../scan ../scan_expected/ >/dev/null 2>&1; then
    echo "PASS"
else
    echo "FAIL"
fi
