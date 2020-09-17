#!/usr/bin/python
#coding=utf-8
import sys
import os
import unittest

# Import project
sys.path.append('yt_album_dl')
import yt_album_dl as yt_dl

class testStringMethods(unittest.TestCase):
    
    def setUp(self):
        #"Le Voyage De Pénélope ":               "Le Voyage De Pénélope",
        pass

    def test_cleanMp3DataTitles(self):
        testDir={}

        testSongsInAlbumOrCompilation={
            "1. Love":                              "Love",
            "2. Lust For Life":                     "Lust For Life",
            "1 - Ernie":                            "Ernie",
            "2 - Cay's Crays":                      "Cay's Crays",
            ": A Walk":                             "A Walk",
            ": Melanine":                           "Melanine",
            "01 DOMINANT":                          "DOMINANT",
            "02 DeKobe":                            "DeKobe",
            "- Symmetry & Ryan Lewis":              "Symmetry & Ryan Lewis",
            "- Blackbear":                          "Blackbear",
            "[] Elephante feat. Jessica Jarrell":   "Elephante feat. Jessica Jarrell",
            "[] Two Feet":                          "Two Feet"
        }

        testPossibleAlbumNames={
            "Based On A True Story (Full Album)":           "Based On A True Story",
            "CRX [Album]":                                  "CRX",
            "The Brown Tape {FULL ALBUM HQ}":               "The Brown Tape",
            "Possibly Drunk <shit>":                        "Possibly Drunk",
            "morning coffee. [lofi / jazzhop / chill mix]": "morning coffee."

        }

        testPossibleTitlesWithinSingle={
            "Do You Feel It? (RICK AND MORTY)":                     "Do You Feel It?",
            "Make It Wit Chu (Virgin Magnetic Material Remix)":     "Make It Wit Chu",
            "THE JUNGLE (Official Lyric Video)":                    "THE JUNGLE",
            "Best Friends (Audio)":                                 "Best Friends",
            "Lust For Life (Full Album) 2017":                      "Lust For Life",
            "Take Care":                                            "Take Care",
            "\"The Beast\"":                                        "The Beast"
        }

        testPossibleTitlesOutofSingle={
            "Hold (Candyland Remix)":                       "Hold (Candyland Remix)",
            "It's All On U (K?d Remix)":                    "It's All On U (K?d Remix)",
            "Farsight":                                     "Farsight",
            "morning coffee":                               "morning coffee",
            "\"Sugar Hill\"":                               "Sugar Hill"
        }

        for testInput, expectedOutput in testSongsInAlbumOrCompilation.items():
            testDir['artist'] = testInput
            testDir = yt_dl.cleanMp3DataTitles(testDir)
            self.assertEqual(testDir['artist'], expectedOutput)

        for testInput, expectedOutput in testPossibleAlbumNames.items():
            testDir['album'] = testInput
            testDir = yt_dl.cleanMp3DataTitles(testDir)
            self.assertEqual(testDir['album'], expectedOutput)

        for testInput, expectedOutput in testPossibleTitlesWithinSingle.items():
            testDir['title'] = testInput
            testDir['type'] = 'single'
            testDir = yt_dl.cleanMp3DataTitles(testDir)
            self.assertEqual(testDir['title'], expectedOutput)

        for testInput, expectedOutput in testPossibleTitlesOutofSingle.items():
            testDir['title'] = testInput
            testDir['type'] = 'album'
            testDir = yt_dl.cleanMp3DataTitles(testDir)
            self.assertEqual(testDir['title'], expectedOutput)

    def test_Title(self):
        testList={
            "grandson":         "Grandson",
            "fuck balls":       "Fuck Balls",
            "Barns Courtney":   "Barns Courtney",
            "ZAYDE WOLF":       "ZAYDE WOLF",
            "けｍ SURF":         "けｍ SURF",
            "ZAYDE WØLF":       "ZAYDE WØLF",
            "the offspring":    "The Offspring",
            "do you feel it?":  "Do You Feel It?",
            "RICK AND MORTY":   "RICK AND MORTY",
            "13 beaches":       "13 Beaches",
        }

        for testInput, expectedOutput in testList.items():
            self.assertEqual(yt_dl.capitaliseTitle(testInput), expectedOutput)

    def test_SplitTitle(self):
        testList={
            # Singles
            "grandson - Best Friends (Audio)":                  ("Grandson", "Best Friends (Audio)"),
            "Barns Courtney - Champion (Official Audio)":       ("Barns Courtney", "Champion (Official Audio)"),
            "Chaos Chaos - Do You Feel It? (RICK AND MORTY)":   ("Chaos Chaos", "Do You Feel It? (RICK AND MORTY)"),
            "ZAYDE WOLF - THE JUNGLE (Official Lyric Video)":   ("ZAYDE WOLF", "THE JUNGLE (Official Lyric Video)"),
            "ZAYDE WØLF - KING":                                ("ZAYDE WØLF", "KING"),

            
            # Album
            "Lana Del Rey - Lust For Life (Full Album) 2017":           ("Lana Del Rey", "Lust For Life (Full Album) 2017"),
            "Fat Freddys Drop - Based On A True Story (Full Album)":    ("Fat Freddys Drop", "Based On A True Story (Full Album)"),
            "Tycho - Dive {Full Album}":                                ("Tycho", "Dive {Full Album}"),
            "Ghostface Killah ~ The Brown Tape {FULL ALBUM HQ}":        ("Ghostface Killah", "The Brown Tape {FULL ALBUM HQ}"),

            # Compilation
            "けｍ SURF - Take Care":                                         ("けｍ SURF", "Take Care"),
            "Justin Stone - 4 am ":                                         ("Justin Stone", "4 Am"),
            "Illenium feat. Liam O'Donnell - It's All On U (K?d Remix)":    ("Illenium Feat. Liam O'Donnell", "It's All On U (K?d Remix)"),
            ".anxious. - Large Americano":                                  (".anxious.", "Large Americano"),

            # Error check
            "SURF Take Care":                False,
            "Justin Stone 4 am ":            False,
            "Illenium fe U (K?d Remix)":     False,
            ".anxirge Americano":            False,
        }

        for testInput, expectedOutput in testList.items():
            self.assertEqual(yt_dl.splitTitleByDelimiter(testInput), expectedOutput)

    def test_cleanFilename(self):
        testNormal={
            "fuck ya's":                                                "fuck yas",
            "Justin Stone - 4 am":                                      "Justin Stone - 4 am",
            "Creaky Jackals feat. WILD - High Tide (Nurko Remix)":      "Creaky Jackals feat WILD - High Tide",
            "jazz & lofi hiphop 🎄":                                   "jazz lofi hiphop",
            "\"Bad Habits\" - The Seige (Lyric Video) [Explicit]":      "Bad Habits - The Seige",
        }

        testNoSpaces={
            "fuck ya's":                                                "fuck_yas",
            "Justin Stone - 4 am":                                      "Justin_Stone_-_4_am",
            "Creaky Jackals feat. WILD - High Tide (Nurko Remix)":      "Creaky_Jackals_feat_WILD_-_High_Tide",
            "jazz & lofi hiphop 🎄":                                   "jazz_lofi_hiphop"
        }

        for testInput, expectedOutput in testNormal.items():
            self.assertEqual(yt_dl.cleanFilename(testInput), expectedOutput)

        for testInput, expectedOutput in testNoSpaces.items():
            yt_dl.downloadSettings['no_spaces'] = True
            self.assertEqual(yt_dl.cleanFilename(testInput), expectedOutput)


if __name__ == '__main__':
    unittest.main()
