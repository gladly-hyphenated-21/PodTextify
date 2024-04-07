# PodTextify
The internet is large, but not unlimited. To train the next generation of AI, we need to move beyond basic text scraping. To this, we propose PodTextify, the first and only dataset of podcasts.



**_Installation_**:
1) clone the repo
2) install [whisper.cpp]([url](https://github.com/ggerganov/whisper.cpp)) with [OpenVino]([url](https://docs.openvino.ai/2024/get-started/install-openvino.html?VERSION=v_2024_0_0&OP_SYSTEM=MACOS&DISTRIBUTION=ARCHIVE))
3) install the requirements

   > pip3 -r requirements.txt



**_Usage_**:

   > main.py --name='(name of podcast, or 'random' for random)' --number=(number of episodes to download) "
