import csv
from os.path import expanduser
import os
import datetime

home = expanduser("~");
text = {
    "red": "\033[91m",
    "yellow": "\033[93m",
    "green": "\033[92m",
    "blue": "\033[94m",
    "bold": "\033[1m",
    "underline": "\033[4m",
    "end": "\033[0m"
}
changeColors = {
    'ADDED': text['green'],
    'DELETED': text['red']
}

def displayChanges(changedSongsIdList, songMap, changeType):
    print("      ============ %s ============") % (changeType)
    changesColor = '%s' % (changeColors[changeType])
    changesMsg = ''
    for changedSongId in changedSongsIdList:
        song = songMap[changedSongId]
        changesMsg += ('      '
            + song['title']
            + ' - '
            + song['artist']
            + ' - '
            + song['album']
            + ' - '
            + song['duration']
            + '\n')
    print(changesColor + changesMsg + text['end'])
    return changesMsg

def generateSongMap(filePath):
    file = open(filePath)
    songList = csv.reader(file)
    songs = {}
    for songEntry in songList:
        song = {}
        songId = songEntry[5]
        song['title'] = songEntry[0]
        song['artist'] = songEntry[1]
        song['album'] = songEntry[2]
        song['duration'] = songEntry[3]
        song['id'] = songId
        songs[songId] = song
    return songs

currentCsvPath = "%s/Downloads/gmusic_lib_snapshot.csv" % (home)
prevCsvPath = "%s/Music/Gmusic/snapshots/previous_snapshot.csv" % (home)
currentSongMap = generateSongMap(currentCsvPath)
prevSongMap = generateSongMap(prevCsvPath)
currentSongsSet = set(currentSongMap.keys())
prevSongsSet = set(prevSongMap.keys())
deletedSongIds = prevSongsSet - currentSongsSet
addedSongIds = currentSongsSet - prevSongsSet
displayChanges(addedSongIds, currentSongMap, 'ADDED')
deletedHistory = displayChanges(deletedSongIds, prevSongMap, 'DELETED')

now = datetime.datetime.now().strftime("%m-%d-%Y %I:%M %p")
fileEntryHeader = "======== Sync on %s ========\n" % (now)
historyPath = "%s/Music/Gmusic/deletedHistory.txt" % (home)
historyFile = open(historyPath, 'a+')
historyFile.write(fileEntryHeader + deletedHistory)
historyFile.close()
print('Deleted songs were recorded')

counterPath = "%s/Music/Gmusic/counter.txt" % (home)
counterFile = open(counterPath, 'r+')
count = int(counterFile.readline())
updatedCount = count + 1
counterFile.seek(0)
counterFile.truncate()
counterFile.write("%s\n" %(updatedCount))
counterFile.close()
nextSnapshotNamePath = "%s/Music/Gmusic/snapshots/snapshot_%s.csv" % (home, updatedCount)
print('Most recent snapshot number: %s') % (updatedCount)

os.rename(prevCsvPath, nextSnapshotNamePath)
os.rename(currentCsvPath, prevCsvPath)
print('Filepaths renamed')
print('Process completed!')
