from deep_translator import GoogleTranslator
print(GoogleTranslator(source='ja',target='en').translate('おめかし・ギア').replace(' ','_'))
