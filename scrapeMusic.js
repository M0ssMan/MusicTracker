function checkHeaders(actual) {
  const expected = new Set(['album', 'artist', 'duration', 'play-count', 'rating', 'title']);
  if (actual.size !== expected.size) {
    throw new Error('unexpected column headers');
  }
  for (const columnTitle of actual.keys()) {
    if (!expected.has(columnTitle)) {
      throw new Error('unexpected column headers');
    }
  }
}

function noQuotes(str) {
   const mod = str.replace(/\"/gi, '\'');
   return mod
}

function convertToCSV(songsMap) {
  let csv = '';
  for (const song of songsMap) {
    const songId = song[0];
    const {title, artist, album, duration, rating} = song[1];
    csv += `"${noQuotes(title)}","${noQuotes(artist)}","${noQuotes(album)}",${duration},${rating},${songId}\n`;
  }
  downloadToFile(csv)
}

function downloadToFile(csv) {
  const blob = new Blob([csv], { type: 'text/csv;charset=UTF-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', 'gmusic_lib_snapshot.csv');
  document.body.appendChild(link);
  link.click();
}

function scrapeSongs() {
  const $firstSongRows = document.querySelectorAll('table.song-table tbody tr.song-row');
  const columnHeaders = new Map();
  if ($firstSongRows.length > 0){
    for (let i = 0; i < $firstSongRows[0].childNodes.length; i++) {
      const columnTitle = $firstSongRows[0].childNodes[i].getAttribute('data-col');
      columnHeaders.set(columnTitle, i);
    }
    checkHeaders(columnHeaders);
  }
  let prevTopSongId;
  let currentTopSongId;
  let guardCounter = 0;
  const songs = new Map();

  function addSongs() {
    const songData = [];
    const $songRows = document.querySelectorAll('table.song-table tbody tr.song-row');
    let $lastRow;
    guardCounter += 1;
    for (const $row of $songRows) {
      const song = {};
      $lastRow = $row;
      song.id = $row.getAttribute('data-id');
      for (const columnHeader of columnHeaders.entries()) {
        const title = columnHeader[0];
        const titleIndex = columnHeader[1];
        song[title] = $row.childNodes[titleIndex].outerText;
      }
      songData.push(song);
    }
    prevTopSongId = currentTopSongId;
    currentTopSongId = songData[0].id;
    songData.map(song => songs.set(song.id, song));
    $lastRow.scrollIntoView(true);
    if (guardCounter < 2000 && prevTopSongId !== currentTopSongId) {
      setTimeout(() => {
        addSongs();
      }, 100);
    }
    else {
      console.log('songs', songs);
      convertToCSV(songs);
    }
  }
  addSongs();
}
scrapeSongs();
