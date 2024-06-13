//replace_environment_variables.js file
const fs = require("fs");

// this will get argument from command line
let config = process.argv[2];

// read template file as string
let template_environment = fs.readFileSync("./src/environments/environment.template.ts").toString();

// for every keys you have defined on environment this will loop over them and replace the values accordingly
Object.keys(process.env).forEach(env_var => {
  template_environment = template_environment.replaceAll(`\${${env_var}}`,process.env[env_var])
});

// if config is given use it on file name.
if(config){
  fs.writeFileSync(`./src/environments/environment.${config}.ts`, template_environment);
  fs.writeFileSync(`./src/environments/environment.development.${config}.ts`, template_environment);
}
else{
  fs.writeFileSync("./src/environments/environment.ts", template_environment);
  fs.writeFileSync("./src/environments/environment.development.ts", template_environment);
}
