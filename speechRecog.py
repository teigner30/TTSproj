import speech_recognition as sr

listening = True

while listening:
    with sr.Microphone() as source:
        r = sr.Recognizer()
        r.adjust_for_ambient_noise(source)
        r.dynamic_energythreshhold = 3000
        try:
            print("listening")
            audio = r.listen(source)
            print("Got audio")
            word = r.recognize_google(audio)
            print(word)
        except sr.UnknownValueError:
            print("I don't know that word")
