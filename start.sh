cd /home/roman/repos/RTbolidozor/

if ! pidof -x RTbolidozor_server.py  > /dev/null; then
    python3 RTbolidozor_server.py > /dev/null &
fi


if ! pidof -x RTbolidozor_analyzer.py  > /dev/null; then
    python3 RTbolidozor_analyzer.py > /dev/null &
fi

