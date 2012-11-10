<!DOCTYPE html>
<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js"> <!--<![endif]-->
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <title>Login</title>
        <meta name="viewport" content="width=device-width">
    </head>
    <body>
        <!--[if lt IE 7]>
            <p class="chromeframe">You are using an outdated browser. <a href="http://browsehappy.com/">Upgrade your browser today</a> or <a href="http://www.google.com/chromeframe/?redirect=true">install Google Chrome Frame</a> to better experience this site.</p>
        <![endif]-->

		<p>${msg}</p>

		<p>Please login:</p>
        <form action="${url}" method="post">
          <input type="hidden" name="came_from" value="${came_from}"/>
          Login <input type="text" name="login" value="${login}"/><br/>
          Password <input type="password" name="pwd"
                 value="${pwd}"/><br/>
          <input type="submit" name="submit" value="Log In"/>
        </form>
    </body>
</html>


