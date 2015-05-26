If you don’t already have one, request a Cloud Foundry account and download the Cloud Foundry CLI according to the instructions here:
https://docs.18f.gov/getting-started/setup/

Then, target the hourglass space inside the oasis org:
`cf target -o oasis -s hourglass`

You can edit the app attributes in the `manifest.yml` file, including what domains the site deploys to, how many instances are running, and how much memory they have. 

Pushing to the Dev Server:

This you can push to directly, with just:
`cf push calc-dev`.

Pushing to Production with Blue-Green Deploys

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




