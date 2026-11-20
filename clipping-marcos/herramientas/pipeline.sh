# Uso: pipeline.sh <dir> <nombre>   (espera <dir>/<nombre>.mp4)
S=/tmp/claude-0/-home-user-Umbral/103299cb-7cc6-5615-898c-8dde6d176f21/scratchpad
D=$1; N=$2
ffmpeg -loglevel error -y -i $D/$N.mp4 -vn -ac 1 -ar 16000 $D/audio.wav || exit 1
ffmpeg -loglevel error -i $D/audio.wav -af "asetnsamples=16000,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=$D/rms.txt" -f null -
cd $S/work && python3 -I transcribe.py $D/audio.wav $D/transcript.txt small $S/models
echo PIPE_DONE
