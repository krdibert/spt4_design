# spt4_masks

Right now what is in here is the mask generation code for SPT4 220 GHz CPW masks. I'm working on making this more user friendly. For now I would suggest not changing anything except the settings files and the create_mask scripts.

To get started try running triangle.py in the cpw_220 folder. It will generate a triangular sector on a 4-inch wafer. This isn't ready for fab because the frequency scheduling hasn't been done yet!

## Warning
Don't accidentally commit .gds files to this repo! Save them to an outside directory.
