### Deploying to Cloud Foundry
###### Only of interest to 18F team members
If you don’t already have one, request a Cloud Foundry account in #devops in Slack and download the Cloud Foundry CLI according to the instructions here:
https://docs.18f.gov/getting-started/setup/

#### CF Structure
- Organization: `oasis`
- Spaces: `calc-dev`, `calc-prod`
- Apps:
  - calc-dev space:
    - calc-dev
  - calc-prod space:
    - calc-deploy
    - calc-prod
- Routes:
  - calc-dev.18f.gov -> calc-dev space, calc-dev app
  - calc-prod.18f.gov -> calc-prod space, calc-prod app
  - calc-deploy.18f.gov -> calc-prod space, calc-deploy app
  - calc.gsa.gov -> calc-prod space, calc-prod or calc-deploy spaces
  
To start, target the org and space you want to work with. For example, if you wanted to work with the production space:
`cf target -o oasis -s calc-prod`

You can edit the app attributes in the `manifest.yml` file, including what domains the site deploys to, how many instances are running, and how much memory they have. 

#### Dev Server
The development server updates automatically when changes are merged into the master branch. Check out `.travis.yml` for details.

Should you need to, you can push directly to calc-dev.18f.gov with the following:
`cf push calc-dev`.
Remember to target the `calc-dev` space first.

#### Your Own Server

If you want to deploy to your own sandbox, e.g. for the purpose of deploying a branch you're working on, see the wiki page on [How to Deploy to your Sandbox](https://github.com/18F/calc/wiki/How-to-Deploy-to-your-Sandbox).

#### Production Servers
##### Pushing to Production with Blue-Green Deploys

Full CF docs are here: http://docs.cloudfoundry.org/devguide/deploy-apps/blue-green.html

At any time, you can see which urls are mapped to which apps by running

`cf apps`

Lets say that calc-prod is mapped to calc.gsa.gov. We’ll deploy to the calc-deploy app first: 

`cf push calc-deploy`

This will push to calc-deploy.18f.gov. Make sure everything looks good.

Next, map calc.gsa.gov to the app you just pushed, using:

`cf map-route calc-deploy calc.gsa.gov`

Then unmap calc.gsa.gov from the original app, using: 

`cf unmap-route hourglass-prod calc.gsa.gov`

Your changes are now launched! How easy was that?




