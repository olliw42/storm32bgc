mkspiffs  -c data -p 256 -b 4096 -s 131072 storm32web.spiffs.bin -d 5 

esptool -cd ck -cb 115200 -cp %1 -ca 0xDB000 -cf storm32web.spiffs.bin