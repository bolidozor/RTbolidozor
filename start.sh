cd /home/roman/repos/RTbolidozor/

if ! pidof -x RTbolidozor_server.py  > /dev/null; then
    python RTbolidozor_server.py > /dev/null &
fi


if ! pidof -x RTbolidozor_analyzer.py  > /dev/null; then
    python RTbolidozor_analyzer.py > /dev/null &
fi

