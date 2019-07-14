import csv
import os
import datetime

home = os.path.expanduser("~");
appPath = "%s/Music/GMusic/MusicTracker" % (home)
deletedSongsCsvPath = "%s/gmusic_deleted_songs.csv" % (appPath)
queuePath = "%s/queue" % (appPath)
snapshotsPath = "%s/snapshots" % (appPath)
lastTimestampPath = "%s/last_timestamp.txt" % (appPath)

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

def filterForSnapshots(listOfFileNames):
    onlySnapshotTimestamps = []
    for fileName in listOfFileNames:
        fileNameParts = fileName.split('_')
        if fileNameParts[0] == 'gmusic':
            snapshotTimestamp = int(fileNameParts[2].split('.')[0])
            onlySnapshotTimestamps.append(snapshotTimestamp)
    return sorted(onlySnapshotTimestamps)

def displayChanges(changedSongsIdList, songMap, changeType, timestamp):
    print("      ============ %s ============") % (changeType)
    convertedTimestamp = timestamp / 1000
    now = datetime.datetime.fromtimestamp(convertedTimestamp).strftime("%m-%d-%Y %I:%M %p")
    dateStr = "            %s\n" % (now)
    print(dateStr)
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

def generateSongMap(filePath, isDeletedMap = False):
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
        if isDeletedMap:
            song['timestamp'] = songEntry[4]
    file.close()
    return songs

def writeUpdatedDeletedSongsToCsv(songList):
    result = []
    for song in songList:
        songDetailsList = [
            song['title'],
            song['artist'],
            song['album'],
            song['duration'],
            song['timestamp'],
            song['id'],
        ]
        result.append(songDetailsList)
    with open(deletedSongsCsvPath, "w+") as deletedSongsCsv:
        csvWriter = csv.writer(deletedSongsCsv)
        csvWriter.writerows(result)

def updateDeletedSongs(songMap, deletedSongMap):
    for existingSong in songMap.values():
        for deletedSong in deletedSongMap.values():
            if existingSong.has_key(deletedSong['id']):
                deletedSongMap.pop(deletedSong['id'], None)
            existingSongMash = existingSong['title'] + existingSong['artist']
            deletedSongMash = deletedSong['title'] + deletedSong['artist']
            if existingSongMash == deletedSongMash:
                deletedSongMap.pop(deletedSong['id'])

def addDeletedSongsToMap(deletedSongMap, deletedSongIds, songMap, snapshotTimestamp):
    for songId in deletedSongIds:
        deletedSongMap[songId] = songMap[songId];
        deletedSongMap[songId]['timestamp'] = str(snapshotTimestamp)

def snapshotAnalysis(snapshotTimestamp, previousTimestamp, deletedSongMap):
    currentCsvPath = "%s/gmusic_snapshot_%s.csv" % (queuePath, snapshotTimestamp)
    prevCsvPath = "%s/gmusic_snapshot_%s.csv" % (snapshotsPath, previousTimestamp)
    currentSongMap = generateSongMap(currentCsvPath)
    prevSongMap = generateSongMap(prevCsvPath)
    updateDeletedSongs(currentSongMap, deletedSongMap)
    currentSongsSet = set(currentSongMap.keys())
    prevSongsSet = set(prevSongMap.keys())
    deletedSongIds = prevSongsSet - currentSongsSet
    addedSongIds = currentSongsSet - prevSongsSet
    displayChanges(addedSongIds, currentSongMap, 'ADDED', snapshotTimestamp)
    deletedHistory = displayChanges(deletedSongIds, prevSongMap, 'DELETED', snapshotTimestamp)
    addDeletedSongsToMap(deletedSongMap, deletedSongIds, prevSongMap, snapshotTimestamp)
    updatedCurrentCsvPath = "%s/gmusic_snapshot_%s.csv" % (snapshotsPath, snapshotTimestamp)
    os.rename(currentCsvPath, updatedCurrentCsvPath)
    print("snaphot processed\n\n")

queueFilesList = os.listdir(queuePath)
snapshotTimestamps = filterForSnapshots(queueFilesList)

print('snapshot timestamps to process')
print(snapshotTimestamps)

deletedSongMap = generateSongMap(deletedSongsCsvPath, True)

lastTimestampFile = open(lastTimestampPath, 'r+')
lastTimestamp = int(lastTimestampFile.readline())

for timestamp in snapshotTimestamps:
    snapshotAnalysis(timestamp, lastTimestamp, deletedSongMap)
    lastTimestamp = timestamp

# <========= ADD BACK =============
lastTimestampFile.seek(0)
lastTimestampFile.truncate()
lastTimestampFile.write(str(lastTimestamp))
lastTimestampFile.close()


deletedSongList = [v for v in deletedSongMap.values()]
deletedSongList.sort(key=lambda x: x['album'])
writeUpdatedDeletedSongsToCsv(deletedSongList)
print("Success!")
