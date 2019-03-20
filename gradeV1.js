var fs = require('fs');

fs.readFile('input.txt', 'utf8', function(err, data) {
    if (err) throw err;
    var student;
    var readingAnswer = false;
    var answers = [];
    var students = new Map();
    data.split('\n').forEach(line => {
        if (line == '') {
            return;
        }
        if (line.startsWith('Answer Key:')) {
            readingAnswer = true;
            return;
        }
        if (line.startsWith('Student')) {
            readingAnswer = false;
            student = line.replace('Student', '').replace(':' ,'').replace(' ', '');
            return;
        }
        if (readingAnswer) {
            answer = line.split(' /');
            answers.push(answer);
            return;
        }
        if (student) {
            if (students.has(student)) {
                students.set(student, students.get(student) + line);
            } else {
                students.set(student, line);
            }
        }
    });

    students.forEach((value, key, map) => {
        var score = 0;
        var subjects = new Map();
        var questions = new Map();
        value.split('').forEach((answer, index) => {
            var correctAnswer = answers[index][0];
            var subjectKey = answers[index][1];
            var questionKey = answers[index][2];
            var correct = answer == correctAnswer ? 1 : 0;
            score += correct;

            var subject = subjects.has(subjectKey) ? subjects.get(subjectKey) : { total : 0, correct : 0 };
            subject.total++;
            subject.correct += correct;

            var question = questions.has(questionKey) ? questions.get(questionKey) : { total : 0, correct : 0 };
            question.total++;
            question.correct += correct;

            questions.set(questionKey, question);
            subjects.set(subjectKey, subject);
        });

       var contents = `Student ${key}:\n`;
        contents += `Raw Score ${score}/${value.length}\n`;
        contents += `\n`;
        contents += `Score Breakdown by Subject:\n`;
        subjects.forEach((value, key) => {
            contents += `${key}: ${value.correct}/${value.total}\n`;
        })
        contents += `\n`;
        contents += `Score Breakdown by Question:\n`;
        questions.forEach((value, key) => {
            contents += `${key}: ${value.correct}/${value.total}\n`;
        })
        contents += `\n`;

        fs.appendFile('output.txt', contents);
    });
});
