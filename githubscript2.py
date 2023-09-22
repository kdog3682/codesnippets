import base64
import github
from base import *
from next import *

def getToken(key = None):
    ref = {
        None: env.kdogGithubToken,
        'kdog3682': env.kdogGithubToken,
    }
    return ref[key]

class Github:
    def view(self):
        contents = self.getRepoContents()
        pprint(contents)
    

    def __init__(self, key=None):
        self.token = getToken(key)
        self.github = github.Github(self.token)
        self.user = self.github.get_user()
        self.username = self.user.login

    def doAuthentication(self, repoName):
        command = (
            'curl -H "Authorization: token '
            + self.token
            + '" --data \'{"name":"'
            + repoName
            + "\"}' https://api.github.com/user/repos"
        )
        os.system(command)
        blue('Authenticated', repoName)

    def setRepo(self, repoName, private=False):

        if '/' in repoName:
            repoName = repoName.split('/')[-1]

        try:
            self.repo = self.user.get_repo(repoName)
        except Exception as e:
            checkErrorMessage(e, 'Not Found')

            try:
                self.repo = self.user.create_repo(
                    repoName, private=private
                )
            except Exception as e:
                checkErrorMessage(e, 'Repository creation failed')

                self.doAuthentication(repoName)
                sleep(1)
                self.repo = self.github.get_repo(repoName)

        blue('Successfully set the repo', repoName)
        return self.repo

    def getRepoContents(self, repo=None, path=''):
        if not repo: repo = self.repo
        try:
            return repo.get_contents(path, ref=repo.default_branch)
        except Exception as e:
            message = getErrorMessage(e)
            if message == 'This repository is empty':
                return []
            raise e
        

    def getRepo(self, x):
        if isString(x):
            return self.user.get_repo(x)
        return x

    def getRepos(self):
        return self.user.get_repos()
    
    

def prompt(*args, aliases=None):
    for arg in args:
        if arg:
            if isString(arg):
                print(arg)
            else:
                pprint(arg)
    a = input()
    return aliases.get(a, a) if aliases else a

def require(x, message):
    if x == None or x == '':
        raise Exception(message)

def choose(x):

    for i, item in enumerate(x):
        print(i + 1, item)

    print('')
    answer = input()
    if not answer:
        return 

    indexes = answer.strip().split(' ')
    value = [x[int(n) - 1] for n in indexes]
    return smallify(value)


class GithubController(Github):

    def run(self):

        store = []
        repos = self.getRepos()

        def runner(prevAnswer=None):
            if prevAnswer:
                repo = repos[int(prevAnswer) - 1]
            else:
                repo = choose(repos)
            if not repo:
                return finish()
            contents = self.getRepoContents(repo)
            if not contents:
                store.append(['deleteRepo', repo])
                return runner()

            aliases = {
                'd': 'deleteRepo',
                'v': 'viewRepo',
            }

            answer = prompt(contents, aliases=aliases)
            if answer:
                if isNumber(answer):
                    return runner(answer)
                store.append([answer, repo])
                runner()
            else:
                return finish()

        def finish():
            if not store:
                return 

            prompt(store)
            for methodKey,repo in store:
                getattr(self, methodKey)(repo)

            blue('Finished')

        
        runner()


    def deleteRepo(self, x):
        repo = self.getRepo(x)

        if test('kdog3682|2023', repo.name):
            if not test('kdog3682-', repo.name):
                return red('Forbidden Deletion', repo.name)

        repo.delete()
        blue('Deleting Repo', repo.name)
        localName = re.sub('kdog3682-', '', repo.name)
        localDir = npath(rootdir, localName)
        rmdir(localDir, ask=True)


    def createLocalRepo(self, dirName, private=False):
        dirName = dirName.upper()
        self.setRepo(dirName, private)
        dir = npath(rootdir, dirName)

        remote = 'origin'
        username = self.username

        mkdir(dir)
        chdir(dir)

        if not isfile('README.md') and empty(os.listdir(dir)):
            write('README.md', 'howdy from ' + dir)

        s = f"""
            cd {dir}
            git init
            git add .
            git commit -m "first commit"
            git branch -M main
            git remote add {remote} git@github.com:{username}/{dirName}.git
            git push -u {remote} main 
        """
        result = SystemCommand(s, dir=dir)
        print({'success': result.success, 'error': result.error})

    def upload(self, file, content=None):
         updateRepo(self.repo, file, content)
    


def updateRepo(repo, file, content=None):
    if not content:
        content = raw(file)

    branch = repo.default_branch
    path = tail(file)

    try:
        return repo.create_file(
            path=path,
            message=f"Upload {file}",
            content=content,
            branch=branch,
        )

    except Exception as error:
        reference = repo.get_contents(file, ref=branch)
        return repo.update_file(
            path=reference.path,
            message="Update file content",
            content=content,
            sha=reference.sha,
            branch=branch,
        )

    

def gitPush(dir, commitMessage='autopush'):

    s = f"""
        cd {dir}
        git add .
        git commit -m "{commitMessage}"
        git push
    """
    SystemCommand(s, dir=dir)




def getErrorMessage(e):
    s = search('"message": "(.*?)"', str(e))
    return re.sub('\.$', '', s)

def archived():
    pass
    # g.createLocalRepo('RESOURCES', private=True)
    # g.run()

def main():
    g = GithubController()
    g.setRepo('codesnippets')
    g.upload('/home/kdog3682/PYTHON/githubscript2.py')
    g.view()


def checkErrorMessage(e, s):
    if getErrorMessage(e) != s:
        warn('Invalid Error', str(e))

main()
