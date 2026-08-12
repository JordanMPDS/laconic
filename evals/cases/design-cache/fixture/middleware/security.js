// Added after the 2024 audit finding: an account page had been served to the
// wrong user out of an intermediary cache. The remediation was to forbid
// caching, and it was applied app-wide because that was the fastest way to
// close the finding before the deadline.
//
// It has never been revisited. It applies to /p as well as /account.
module.exports = function security(req, res, next) {
  res.set('Cache-Control', 'no-store, no-cache, must-revalidate, private');
  res.set('Pragma', 'no-cache');
  res.set('X-Frame-Options', 'DENY');
  res.set('X-Content-Type-Options', 'nosniff');
  next();
};
