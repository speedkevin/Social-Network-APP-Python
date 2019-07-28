var mongoose = require('mongoose');
var bcrypt = require('bcryptjs');

// We don't need connect here because connect has already existed in app.js
// mongoose.connect('mongodb://localhost/loginapp');
// var db = mongoose.connection;

// User Schema
var UserSchema = mongoose.Schema({
  // Linebot
  line_userid: String,
  username: {
    type: String,
    index: true
  },
  password: String,
  email: String,
  name: String,
  resetPasswordToken: String,
  resetPasswordExpires: Date,
  self: {
      picture: String,
      location: String,
      sex: String,
      orientationMale: Boolean,
      orientationFemale: Boolean,
      orientationThird: Boolean,
      intro: String
  },
  theone: {
      picture: String,
      location: String
  },
  settings: {
      account_status: String
  }
});

// reset password
/*
UserSchema.pre('save', function(next) {
  var user = this;
  var SALT_FACTOR = 5;

  if (!user.isModified('password')) return next();

  bcrypt.genSalt(SALT_FACTOR, function(err, salt) {
    if (err) return next(err);

    bcrypt.hash(user.password, salt, null, function(err, hash) {
      if (err) return next(err);
      user.password = hash;
      next();
    });
  });
});
*/

// Will be named as "users" on the collection name on mlab
var User = module.exports = mongoose.model('User', UserSchema);

module.exports.createUser = function(newUser, callback){
  bcrypt.genSalt(10, function(err, salt) {
    bcrypt.hash(newUser.password, salt, function(err, hash) {
        // Store hash in your password DB.
        newUser.password = hash;
        newUser.save(callback);
    });
  });
}

// Autehnticate function
module.exports.getUserByUsername = function(username, callback){
  var query = {username: username};
  User.findOne(query, callback); // mongoose method
}

// Autehnticate: serialize
module.exports.getUserById = function(id, callback){
  User.findById(id, callback); // mongoose method
}

// Autehnticate function
module.exports.comparePassword = function(candidatePassword, hash, callback){
  bcrypt.compare(candidatePassword, hash, function(err, isMatch) {
    if(err) throw err;
    callback(null, isMatch);
  });
}
