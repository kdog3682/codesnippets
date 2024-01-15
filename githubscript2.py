import github
from utils import *

class Github:
    
    def view(self, path='', file=''):
        contents = self.getRepoContents(path=path)
        if file:
            f = lambda x: tail(x.path) == tail(file)
            content = find(contents, f)
            if content:
                blue_colon('content', content)
                blue_colon('path', content.path)
                blue_colon('text', content.decoded_content.decode('utf-8'))
            else:
                print('no content found')
                print('original contents:')
                pprint(contents)
        else:
            pprint(contents)
    

    def __init__(self, key=None):
        self.token = env.github_token_ref[key]
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
        blue_colon('Authenticated', repoName)

    def setRepo(self, repoName, private=False, create=False):

        if '/' in repoName:
            repoName = repoName.split('/')[-1]

        print('repoName', repoName)
        try:
            self.repo = self.user.get_repo(repoName)
        except Exception as e:
            checkErrorMessage(e, 'Not Found')
            if not create:
                raise Exception('The repo doesnt exist and create is False')

            try:
                self.repo = self.user.create_repo(
                    repoName, private=private
                )
            except Exception as e:
                checkErrorMessage(e, 'Repository creation failed')

                self.doAuthentication(repoName)
                sleep(1)
                self.repo = self.github.get_repo(repoName)

        blue_colon('Successfully set the repo', repoName)
        return self.repo

    def getRepoContents(self, repo=None, path='', recursive = 0):
        if not repo: 
            repo = self.repo

        try:
            ref = repo.default_branch
            contents = repo.get_contents(path, ref=ref)
            if not recursive:
                return contents

            store = []
            while contents:
                content = contents.pop(0)
                if is_private_filename(content.path):
                    continue
                if content.type == "dir":
                    items = repo.get_contents(content.path, ref=ref)
                    contents.extend(items)
                else:
                    store.append(content)
            return store

        except Exception as e:
            raise e

    def getRepo(self, x):
        if isString(x):
            return self.user.get_repo(x)
        return x

    def getRepos(self):
        return self.user.get_repos()
    
    def open_url(self):
        view(self.repo.html_url)
    

class GithubController(Github):

    def download(self, url):
        r = '/'
        url = url.replace('https://', '')
        p = re.split(r, url)
        user = p[1]
        repo = p[2]
        target = p[-1]
        folderName = prompt3('choose a folder name for the repo: ' + target, fallback = target)
        query = user + '/' + repo
        repo = self.github.get_repo(query)
        items = self.getRepoContents(repo, target, recursive = 1)
        items = antichoose(items)
        write = writef(dldir, user + '-' + folderName)
        store = []
        t = str(timestamp())
        for item in items:
            store.append(t + ' ' + write(item.path, item.decoded_content.decode("utf-8")))

        append('/home/kdog3682/2024/files.log', join(store))
    	

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

            blue_colon('Finished')

        
        runner()


    def deleteRepo(self, x):
        repo = self.getRepo(x)

        if test('kdog3682|2023', repo.name):
            if not test('kdog3682-', repo.name):
                return red('Forbidden Deletion', repo.name)

        repo.delete()
        blue_colon('Deleting Repo', repo.name)
        localName = re.sub('kdog3682-', '', repo.name)
        localDir = npath(rootdir, localName)
        rmdir(localDir, ask=True)


    def upload_file(self, file, content=None, name = None):
         return update_repo(self.repo, file, content, name = None)

    def upload_directory(self, dir, name = None):
        files = os.listdir(dir)
        dirname = head(dir)
        for file in files:
            p = Path(dir, file)
            if p.is_dir():
                continue

            content = pprint().read_bytes()
            name = str(Path(dirname, file))
            update_repo(self.repo, content = content, name = path)
    

    def initialize_local_directory(self, dir):
        """
            turns the given directory into a git repo
            optionally writes gitignore based on the files present
        """

        if is_git_directory(dir):
            return printf(""" "$dir" is already a git directory""")

        if not is_dir(dir):
            answer = inform("""
                $dir is not an existant directory
                would you like to create it?
            """, accept_on_enter = 1)
            if not answer:
                return 
            else:
                mkdir(dir)

        repo_name = ask("repo_name", tail(dir))
        address = f"{self.username}/{repo_name}"

        system_command(f"""
            cd {dir}
            git init
            git add .
            git commit -m "first commit"
            git branch -M main
            git remote add origin git@github.com:{address}.git
            git push -u origin main 
        """, confirm = 1)

        write_gitignore_file(dir)
        view(self.repo.html_url)

def update_repo(repo, file = "", content=None, name = None):
    if not content:
        content = read_bytes(file)

    branch = repo.default_branch
    path = name or tail(file)

    try:
        return repo.create_file(
            path=path,
            message=f"uploading {path}",
            content=content,
            branch=branch,
        )

    except Exception as e:
        print(str(e))
        reference = repo.get_contents(path, ref=branch)
        assert(reference)

        return repo.update_file(
            path=reference.path,
            message="Update file content",
            content=content,
            sha=reference.sha,
            branch=branch,
        )


def run(fn, *args, **kwargs):
    controller = GithubController(key='kdog3682')
    with blue_sandwich():
        print('Kwargs', kwargs)
        print('Running the Function', fn)
        print('Github Instance Initialized', controller)
    fn(controller, *args, **kwargs)


def example(g):
    g.run() # press d to delete the chosen repo
            # the options will shown up in the aliases

def example(g):
    """
        We enter the codesnippets repo
        We upload a file into it
        We view the contents of the repo
        We open the url
    """
    g.setRepo('codesnippets')
    print(g.upload_file('/home/kdog3682/PYTHON/githubscript2.py', name = "abc/foosdfsdf.py"))
    # g.view()
    # g.open_url()


if __name__ == "__main__":
    run(example)
