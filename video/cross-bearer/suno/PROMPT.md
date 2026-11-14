# Suno용 프롬프트 — '십자가의 전달자' 오프닝 60초 연주곡

합성한 현재 음악 대신 실제 악단 같은 소리를 원할 때 쓴다. Suno 생성은 본인 계정으로 직접 해야 한다.
`bitwize-music` 플러그인의 `suno-engineer` 지침(연주곡: Instrumental 켜기, 스타일 상자에 장르·악기·분위기·템포, 가사 상자에는 구조 태그만, 태그마다 연주 지시 한두 단어)에 맞춰 작성했다.

## 설정

- Advanced Mode, **Instrumental: On**, **Variety: Off** (켜면 Suno가 스타일 상자를 고쳐 쓴다)
- 길이는 1분 안팎으로 나오게 여러 번 생성해 고른다. 정확히 60초로는 안 나오므로 받은 뒤 맞춘다.
- 아래 스타일 문구의 침묵·타악 지시는 v5 컷 기준이다. v6는 53.5초 한 번만 크게 열리면 된다.

## Style Box

```
Epic cinematic orchestral film score, instrumental, D minor resolving to D major, 60 BPM, slow and solemn. Solo piano and low cello drone open in darkness; strings join; timpani and low brass for a storm; a hushed wordless choir; a complete silence before the climax; solo cello over an accelerating timpani roll; then full orchestra, French horns, choir and cymbals in a triumphant major key. Reverent, sacred, goosebump-inducing, wide concert hall reverb, huge dynamic range.
```

## Exclude Styles

```
vocals, lyrics, singing words, drums kit, electric guitar, synth, EDM, trap, pop beat, lo-fi
```

## Lyrics Box (구조 태그만)

```
[Intro - dark, solitary piano]

[Theme - four-note motif, low strings]

[Build - hopeful, rolling strings]

[Storm - timpani, low brass, urgent]

[Interlude - hushed wordless choir]

[Break - total silence]

[Bridge - solo cello, timpani roll rising]

[Climax - full orchestra, major key, triumphant]

[Outro - horns carry the theme, final chord]

[End]
```

## 영상 큐 (받은 음원을 맞출 기준, v6 컷)

| 시간 | 영상 | 음악 |
|---|---|---|
| 0–13초 | 스데반, 다메섹 길, 하늘의 빛 | 어둡고 고요하게, 피아노 중심 |
| 13–21초 | 아나니아, 금빛 새벽 항해 | 현악이 들어오며 밝아짐 |
| 21–29초 | 파선, 감옥 | 가장 어두운 구간 |
| 29–45초 | 아덴, 밀레도, 결박, 로마 | 꾸준히, 점점 비워짐 |
| 45–49초 | 마지막 새벽 | 거의 멈춤 |
| 49–53.5초 | 갈보리를 오름 | 첼로 독주 |
| **53.5초** | 빛이 번짐 | **정점, 장조로 전환** |
| 54.5–58.5초 | 캠퍼스 | 주제를 장조로 |
| 58.5–65초 | 제목 | 마지막 화음, 5초 넘게 자연스럽게 사라짐 |

음원을 `video/cross-bearer/suno/`에 올려 주면 정점을 53.5초에 맞춰 자르고, 플러그인으로 마스터링해 영상에 입힌다. '십자가의 전달자' 원곡 선율은 프롬프트에 넣지 않았다.
