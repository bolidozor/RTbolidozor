# RTbolidozor
A real-time meteor event visualiser in web browser. 





## Instalace na stanici

mkdir ~/repos && cd ~/repos
sudo apt-get install python-websocket
git clone https://github.com/bolidozor/RTbolidozor.git RTstation
cd RTstation && git checkout station

### uprava radio-observeru:

do souboru /src/BolidRecorder.cpp před (********METEOR DETECTED********) (řádek ...) přidat:

				cout << "met;" << t << ";"
					 << noise_ << ";"
					 << peakFreq_ << ";"
					 << magnitude_ << ";"
					 << peakFreq_ - (maxDetectFq_ - minDetectFq_) / 4 << ";"
					 << peakFreq_ + (maxDetectFq_ - minDetectFq_) / 4 << ";"
					 << 0 << ";"
					 << fftSamplesToRaw(nextSnapshot_.length) << "#" << endl;


a ve složce radio-observer zkompilovat pomocí make. 
do souboru start.sh přidat za radio-obrerver "| python ~/repos/RTstation/RTstation.py"