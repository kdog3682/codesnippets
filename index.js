var fs = require('fs');
var debug = process.argv.some(value =>  value.includes('debug'));

fs.readFile('input.txt', 'utf8', function(err, data) {
    if (err) throw err;
    var readingStudents;
    var readingAnswer = false;
    var answers = [];
    var students = new Map();   if (debug) {
        console.log("Reading file.");
    }
    splitChar = '\n';
    if (splitChar == '\r\n') {
        console.log("ERROR SPLITTING BY WINDOWS LINE ENDINGS")
    }
    data.split(splitChar).forEach(line => {
        if (debug) {
            console.log(`Reading line: ${line}`);
        }
        if(line == '') {
            return;
        }
        if (line.startsWith('Answer')) {
            readingAnswer = true;
            return;
        }
        if (line.startsWith('S1') && readingAnswer) {
            readingAnswer = false;
            readingStudents = true;
            line.split(/\s+/).forEach((value, index) => {
                students.set(index, '');
            });
            return;
        }
        if (readingAnswer) {
            answer = line.split(/\s+/);
            answers.push(answer);
            return;
        }
        if (readingStudents) {
            let row = line.split(/\s+/);
            if (row.length != students.size) {
                throw `Number of answers in the row  does not match the number of students.`
            }
            line.split(/\s+/).forEach((value, index) => {
                students.set(index, students.get(index) + value);
            });
        }
    });

    if (debug) {
        console.log('Answers:');
        console.log(answers);
        console.log('Students:');
        console.log(students);
    }

    students.forEach((value, key, map) => {
        // var score = 0;
        var subjects = new Map();
        var questions = new Map();
        var difficulties = new Map();
        value.split('').forEach((answer, index) => {
            var correctAnswer = answers[index][0];
            var subjectKey = answers[index][1];
            var questionKey = answers[index][2];
            var difficultyKey = answers[index][3];
            var correct = answer == correctAnswer ? 1 : 0;
            // score += correct;

            var subject = subjects.has(subjectKey) ? subjects.get(subjectKey) : { total : 0, correct : 0 };
            subject.total++;
            subject.correct += correct;

            var question = questions.has(questionKey) ? questions.get(questionKey) : { total : 0, correct : 0 };
            question.total++;
            question.correct += correct;

            var difficulty = difficulties.has(difficultyKey) ? difficulties.get(difficultyKey) : { total : 0, correct : 0 };
            difficulty.total++;
            difficulty.correct += correct;

            subjects.set(subjectKey, subject);
            questions.set(questionKey, question);
            difficulties.set(difficultyKey, difficulty);
        });

        if (debug) {
            console.log('subjects:');
            console.log(subjects);
            console.log('questions:');
            console.log(questions);
            console.log('difficulties:');
            console.log(difficulties);
        }

       var contents = `Student ${key + 1}:\n`;
        contents += `\n`;
        subjects.forEach((value, key) => {
            if (debug) {
                contents += `${key} - `;
            }
            contents += `${value.correct}/${value.total}\n`;
        })
        contents += `\n\n`;
        questions.forEach((value, key) => {
            if (debug) {
                contents += `${key} - `;
            }
            contents += `${value.correct}/${value.total}\n`;
        })
        contents += `\n\n`;

        difficulties.forEach((value, key) => {
            if (debug) {
                contents += `${key} - `;
            }
            contents += `${value.correct}/${value.total}\n`;
        })
        contents += `\n`;

        fs.appendFileSync('output1.txt', contents);
    });

    answers.forEach((value, number, array) => {
        fs.appendFileSync('output1.txt', `${Array.from(students.values()).map(v => v.charAt(number)).filter(v => v == value[0]).length}/${students.size}\n`);
    });
});
