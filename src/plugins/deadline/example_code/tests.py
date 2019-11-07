
# running deadline command: -ExecuteScript "//cmpa-w-fs04.film.fsu.edu/TestShare/DeadlineRepository10/submission/Integration/Main/JobWriter.py" Maya --write --scene-path "Z:/Projects/VFX/source/16BTH_2020_Arena/assets/Prop/wings2/shd/tmikota/000.001/high/prop_wings2_shd.mb" --job-path "C:/Users/tmikota/AppData/Local/Thinkbox/Deadline10/temp/maya_deadline_info_c3fce79a27.job" --batch-name "prop_wings2_shd"

deadline_command = r'C:\PROGRA~1\Thinkbox\Deadline10\bin\deadlinecommand.exe'

# create a job submission file
job_info_file = ''
# create a plugin info file
plugin_info_file = ''
# https://docs.thinkboxsoftware.com/products/deadline/8.0/1_User%20Manual/manual/command.html
# https://docs.thinkboxsoftware.com/products/deadline/8.0/1_User%20Manual/manual/manual-submission.html#manual-submission-ref-label
output_path = r"\\cmpa-w-fs04.film.fsu.edu\TestShare\Projects\VFX\render\16BTH_2020_Arena\assets\Prop\wings2\shd\tmikota\000.001\high"
scene_path = r"\\cmpa-w-fs04.film.fsu.edu\TestShare\Projects\VFX\source\16BTH_2020_Arena\assets\Prop\wings2\shd\tmikota\000.001\high\prop_wings2_shd.mb"

command = '%s %s %s' % (deadline_command, job_info, plugin_info, scene_path)

print command

