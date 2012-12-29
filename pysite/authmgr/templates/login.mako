<%inherit file="pysite:templates/_layouts/default.mako" />
<%block name="styles">
${parent.styles()}
<style>
label { width: 6em; display: inline-block; }
</style>
</%block>
<%block name="meta_title">Login</%block>

<form action="${url}" method="post">
  <input type="hidden" name="came_from" value="${came_from}"/>
  <label for="login">Login</label> <input id="login" type="text" name="login" value="${login}"/><br/>
  <label for="pwd">Password</label> <input id="pwd" type="password" name="pwd" value="${pwd}"/><br/>
  <input type="submit" name="submit" value="Log In"/>
</form>
<script>
require(['requirejs/domReady!', 'jquery'], function (doc, $) {
	$('#login').focus();
});
</script>

