import sys; sys.stdout.reconfigure(encoding='utf-8')
from pythainlp import word_tokenize

sample = 'ดันวอลล์'
result = ' '.join(word_tokenize(sample, engine='newmm'))
print('Test: "' + sample + '" -> "' + result + '"')

sample2 = 'ดิสออนเนอร์ด'
result2 = ' '.join(word_tokenize(sample2, engine='newmm'))
print('Test: "' + sample2 + '" -> "' + result2 + '"')
