# How the CALC team works

See CONTRIBUTING.md as well for information on automated testing.

## Tools
- Trello
- Github
- Travis CI
- Cloud Foundry

## Workflow
The CALC team uses a loose Scrum framework. We have daily phone standups during 
our two week sprints, for which we do a sprint planning and review and retrospective.

We use a [Trello board](https://trello.com/b/LjXJaVbZ/hourglass) to house our product and release backlogs, as well as to keep track
of progress in the current sprint. Each sprint has its own list of cards. When 
a card is in progress, it should be moved to the "Working" list. After the work
is complete (including documentation and automated tests as appropriate), the card
should be put into the "Acceptance Testing" list until our product owner approves it.

Each card in Trello, before being worked on, should have two lists: Tasks and Acceptance 
Criteria. Tasks are defined during sprint planning and reflect all of the work that will
need to take place to complete the feature. Where appropriate, mention team members in the
task to assign it. 

Acceptance Criteria should outline what the user will see and experience in order for the 
feature to be considered complete.

If a card is started in a sprint but not finished, it is placed back into the Release Backlog 
for reprioritization in a following sprint.

Before each sprint planning, our product owner sorts the cards in the Release Backlog based on 
their priority.

Design documents should be attached to their relevant cards for reference.

### Git Workflow

We use the [feature branch model](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow). 
Make sure to delete feature branches after they've been merged into master so that we have
a clean list of branches.

Travis CI runs automated builds that run the full test suite with each commit on a pull request. At the time
of writing, there are some periodic false failures. Tests should never be ignored if they fail. Tests must be passing 
before merging into master. Rerun tests if necessary.

### Deployment
See deploy.md for technical details.

Before each sprint planning, all changes that are to be included in the sprint should be merged into
master and updated on the calc-dev Cloud Foundry app. This is so that our product owner can demo 
the work before accepting it.

We do blue-green deploys to our production Cloud Foundry instances after each sprint. There's no reason
not to do deploys more often if desired, as long as master is kept clean.

## Technical Criteria
Each set of code changes should:
- have the full automated test suite run against them before pushing to origin
- contain Selenium and Python unit tests where applicable
- meet [PEP8](https://www.python.org/dev/peps/pep-0008/) standards
