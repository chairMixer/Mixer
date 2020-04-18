# Y-AABB Mixer

demo video available here. https://drive.google.com/open?id=1UT0xPRtmY30uUDI9af4fvQW8j7SUJa6m 

## Setup 
Set up your own python virual envriment.
```bash
virtualenv myenv
source myenv/bin/activate
pip install -r requirement.txt
```
There might be some issue to run open3d, if that happens, please uninstall open3d and compile from source. The detailed instruction can be found here http://www.open3d.org/docs/release/compilation.html.

## Mixer
### mixer.py
mix-n-match chair mixer. The output is the colored obj file (with .mtl), and a screenshot of rendered mesh.

```bash
# generate 10 new chairs to set_a_out folder by sampling parts from set_a
python mixer.py ../set_a/ ../set_a_out/ 10
```

## Other Modules
see detailed inforamation by using `-h`
### chair.py
render a given chair
```bash
python chair.py ../partnet/1173
```
### part.py
render a given part(back 0, seat 1, base 2, armrest 3) of chair
```bash
python part.py ../partnet/1173 0
```
### objViewer.py
render a given (colored) obj file
```bash
python objViewer ../partnet
```
