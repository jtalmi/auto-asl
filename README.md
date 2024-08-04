To ssh into the vm:
`ssh root@69.30.85.91 -p 22162 -i ~/.ssh/<pkpath>`

To copy videos:
`scp -P 22162 -i ~/.ssh/<pkpath> -r root@69.30.85.91:/workspace/segment-anything-2/auto_asl/*.mp4 ./`