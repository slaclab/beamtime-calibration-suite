# results in ../scan will get overridden each run, so no need to delete inbetween
# if ../scan_expected exists, create if doesn't
if [ ! -d "../scan_expected" ]; then
    mkdir ../scan_expected
fi

# copy scan_expected/ to ../scan_expected only if they diff
if ! diff -r scan_expected/ ../scan_expected/ >/dev/null 2>&1; then
    cp -r scan_expected/* ../scan_expected/
fi

python EventScanParallelSlice.py -r 349 > out.txt # output noisy so hide
python EventScanParallelSlice.py -r 349 -f ../scan/EventScanParallel_c0_r349_n1.h5 >> out.txt

if diff -r ../scan ../scan_expected/ >/dev/null 2>&1; then
    echo "PASS"
else
    echo "FAIL"
fi
