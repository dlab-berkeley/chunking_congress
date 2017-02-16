#!/usr/bin/python
import sys, re, json

## filename = sys.argv[1]

## we'll try and make this as 'stateless' as is possible,
## by which we mean that the result of one lines read
## effects subsequent lines reads as minimally as possible.
## Though, to be clear, it is not state-free. We have flags
## for inspeech, inbody, contentsTop, etc.
## In addition, this will be a 'streaming' implementation
## where we only take one pass at the document,
## and collect all data along the way
## (as  might be expected of a reader).

## This script was written by the combined effort of Jeff Gordon and Jake Ryland Williams.
## I have made only minor edits for pedagogical purposes. -- Nick Adams


def parse_file(filename):

    speaker = ""
    surname = ""
    chains = []
    speeches = [{'surname': "", 'speech': "", 'speaker': "", 'previous_surname': "", "previous_speaker": "", 'committee': "", 'congress': "", 'date': ""}]
    speakers = {}
    junk = []
    inspeech = 0
    inbody = 0
    newspeaker = 0
    contentsTop = 0
    contentsBottom = 0
    contents = ""
    f = open(filename,"r")

    #extract metadata
    orig_filename = re.split('docs/', filename)[1]
    date = re.split('Monday, |Tuesday, |Wednesday, |Thursday, |Friday, |Saturday, |Sunday, ',orig_filename)[1].split('.')[0]
    congress = re.split('_',orig_filename)[0]
    committee = re.split('_',orig_filename)[2]

    for line in f:
        newspeaker = 0

        ## The computer start each line with the assumption that (in a state where) there is not a newspeaker. Then, if it is under the table of contents
        ## it looks for records beginning with the surnames and titles, which indicate the transitions from one speaker to the next
        if contentsBottom:
            ## speechstarts = re.findall("(?is)    ((?:Senator|Representative|Mr.|Ms.|Mrs.) (?:"+allsurnames+"))\. (.*?)$", line)
            speechstarts = re.findall("(?is)^    ((?:Senator|Representative|Congressman|Congresswoman|Commissioner|Ambassador|Secretary|Admiral|General|Commander|Chief|Colonel|Sergeant|Major|Captain|Governor|The Clerk|Mayor|Minister|Judge|Justice|Chair|Mr.|Ms.|Mrs.|Dr.|Chairman|Chairwoman|Speaker) (?:\S+))\. (.*?)$", line)
            if len(speechstarts):
                previous_surname = surname
                previous_speaker = speaker
                for speaker, speech in speechstarts:
                    nameparts = re.split(" ", speaker)
                    surname = nameparts[-1].lower()
                    if speeches[-1]['speech'] == "":
                        speeches[-1]['surname'] = surname
                        speeches[-1]['speech'] = "    "+speech+"\n"
                        speeches[-1]['speaker'] = speaker
                        speeches[-1]['previous_speaker'] = previous_speaker
                        speeches[-1]['previous_surname'] = previous_surname
                        speeches[-1]['date'] = date
                        speeches[-1]['congress'] = congress
                        speeches[-1]['committee'] = committee
                    else:
                        speeches.append({
                            'surname': surname,
                            'speech': "    "+speech+"\n",
                            'speaker': speaker,
                            'previous_surname': previous_surname,
                            "previous_speaker": previous_speaker,
                            'congress': congress,
                            'date': date,
                            'committee':  committee
                        })
                    inspeech = 1
                    newspeaker = 1
            else:
                speechstarts = re.findall("(?is)^    ((?:The Chairman|The Chairwoman))\. (.*?)$", line)
                if len(speechstarts):
                    previous_surname = surname
                    previous_speaker = speaker
                    for speaker, speech in speechstarts:
                        nameparts = re.split(" ", speaker)
                        surname = nameparts[-1].lower()
                        if speeches[-1]['speech'] == "":
                            speeches[-1]['surname'] = surname
                            speeches[-1]['speech'] = "    "+speech+"\n"
                            speeches[-1]['speaker'] = speaker
                            speeches[-1]['previous_speaker'] = previous_speaker
                            speeches[-1]['previous_surname'] = previous_surname
                            speeches[-1]['date'] = date
                            speeches[-1]['congress'] = congress
                            speeches[-1]['committee'] = committee
                        else:
                            speeches.append({
                                'surname': surname,
                                'speech': "    "+speech+"\n",
                                'speaker': speaker,
                                'previous_surname': previous_surname,
                                "previous_speaker": previous_speaker,
                                'congress': congress,
                                'date': date,
                                'committee':  committee
                            })
                        inspeech = 1
                        newspeaker = 1
                else:
                    ## speechstarts  = re.findall("(?is)^\s*prepared Statement of (.*?(?:"+allsurnames+"))\s*$", line)
                    speechstarts  = re.findall("(?is)^\s*prepared Statement of (.*?(?:.+?))\s*$", line)
                    if len(speechstarts):
                        previous_surname = surname
                        previous_speaker = speaker
                        for speaker in speechstarts:
                            nameparts = re.split(" ", speaker)
                            surname = nameparts[-1].lower()
                            if speeches[-1]['speech'] == "":
                                speeches[-1]['surname'] = surname
                                speeches[-1]['speech'] = ""
                                speeches[-1]['speaker'] = speaker
                                speeches[-1]['previous_speaker'] = previous_speaker
                                speeches[-1]['previous_surname'] = previous_surname
                                speeches[-1]['date'] = date
                                speeches[-1]['congress'] = congress
                                speeches[-1]['committee'] = committee
                            else:
                                speeches.append({
                                    'surname': surname,
                                    'speech': "",
                                    'speaker': speaker,
                                    'previous_surname': previous_surname,
                                    "previous_speaker": previous_speaker,
                                    'congress': congress,
                                    'date': date,
                                    'committee':  committee
                                })
                            inspeech = 1
                            newspeaker = 1
                            
                    else:
                        dubCaps = re.findall("(?s)^    ((?:[A-Z][a-z]+) (?:[A-Za-z\'\-0-9]+){1,3})\. (.*?)$", line)
                        if len(dubCaps):
                            for speaker, speech in dubCaps:
                                print speaker+". \n\n"+speech+"\n\n\n"

        ## speech ends are defined when a new speeches start,
        ## when a total whitespace lines are observed,
        ## or when a single block (not applause or laughter) of bracketed text appears
        ## if newspeaker is active, then we have already processed this line and should just pass
        if not newspeaker:
            if inspeech:
                ## take total whitespace line as an indicator for a speech conclusion
                #if re.search("^\s*\n$",line) or re.search("^\s*\[[^\[\]]*\]\s*$",line):
                #the line below is my attempt to stop applying the whitespace rule
                if re.search("^\s*\[[^\[\]]*\]\s*$",line):
                    if not re.search("(?si)^\s*\[(?:applause\.|laughter\.)]*\]\s*$",line):
                        inspeech = 0
                    keepers = []
                    for ix in range(len(speeches)):
                        speeches[ix]['speech'] = re.sub("^\n+","",speeches[ix]['speech'])
                        speeches[ix]['speech'] = re.sub("\.[A-Z\.\,\s\n]+$",".",speeches[ix]['speech'])
                        speeches[ix]['speech'] = re.sub("\n+$","",speeches[ix]['speech'])

                        if not speeches[ix]['speech'] == "" and not speeches[ix]['speech'] == "\n" and not re.match("(?is)^\s+prepared statement",speeches[ix]['speech']) and not re.match("(?is)^\s+(?:prepared statement|summary statement of|introduction of|opening remarks of|impact of)",speeches[ix]['speech']):
                            keepers.append(speeches[ix])
                        else:
                            junk.append(speeches[ix]['speech'])
                    if len(keepers):
                        chains.append(keepers)                    
                    speeches = [{'surname': "", 'speech': "", 'speaker': "", 'previous_surname': "", "previous_speaker": ""}]

                if inspeech:
                    ## need indicators for an acceptable line
                    if re.search("(?si)^(?:\s*[^\[\]]*(?:\[(?:laughter\.|applause\.)\])?\s*$)",line):
                        speeches[-1]['speech'] = speeches[-1]['speech']+line
                    else:
                        junk.append(line)
            elif surname != "" and speaker != "" and re.search("(?si)^(?:\s*[^\[\]]*(?:\[(?:laughter\.|applause\.)\])?\s*$)",line):
                inspeech = 1
                if speeches[-1]['speech'] == "":
                    speeches[-1]['surname'] = ""
                    speeches[-1]['speech'] = line
                    speeches[-1]['speaker'] = ""
                    speeches[-1]['previous_surname'] = surname
                    speeches[-1]['previous_speaker'] = speaker
                    speeches[-1]['date'] = date
                    speeches[-1]['congress'] = congress
                    speeches[-1]['committee'] = committee
                else:
                    speeches.append({
                        'surname': "",
                        'speech': line,
                        'speaker': "",
                        'previous_surname': surname,
                        "previous_speaker": speaker,
                        'congress': congress,
                        'date': date,
                        'committee':  committee

                    })
            else:
                junk.append(line)


        ## once we hit the "c o n t e n t s," we are in the body and can create our
        ## search for speeches
        if re.search("(?i)c o n t e n t s", line):
            inbody = 1

        ## grab the table of contents and process here
        if contentsTop and re.match("^\s+\-+\s+$",line) and not contentsBottom:
            contentsBottom = 1
        if contentsTop and not contentsBottom:
            contents = contents + line
        if inbody and not contentsTop and re.match("^\s+\-+\s+$",line):
            contentsTop = 1

    f.close()
    ## process and store speeches one more time,
    ## just in case the last batch of speeches
    ## didn't make it to the output gate in the loop
    keepers = []
    for ix in range(len(speeches)):
        speeches[ix]['speech'] = re.sub("^\n+","",speeches[ix]['speech'])
        speeches[ix]['speech'] = re.sub("\.[A-Z\.\,\s\n]+$",".",speeches[ix]['speech'])
        speeches[ix]['speech'] = re.sub("\n+$","",speeches[ix]['speech'])

        if not speeches[ix]['speech'] == "" and not speeches[ix]['speech'] == "\n" and not re.match("(?is)^\s+prepared statement",speeches[ix]['speech']) and not re.match("(?is)^\s+(?:prepared statement|summary statement of|introduction of|opening remarks of|impact of)",speeches[ix]['speech']):
            keepers.append(speeches[ix])
        else:
            junk.append(speeches[ix]['speech'])
        if len(keepers):
            chains.append(keepers)
    
    ## pass the data back to the function call
    #return speakers, chains, junk
    return chains