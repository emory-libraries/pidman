# Author:   Mark Van HOlstyn
# Email:    mvanholstyn@mktec.com
# Version:  $Id: active_record_dbfunction.rb,v 1.2.4.2 2006/06/16 17:52:56 mvanholstyn Exp $
module ActiveRecord
	class ConnectionAdapters::AbstractAdapter		
		# Alias the original quore method so we can still access it.
		alias :orig_quote :quote
		
		########################################################################
		# Overriding the quote method to provide support for database functions.
		# If the passed in value is a DBFunction, this will return:
		#	func_name( arg1[,arg2...] )
		# If this is not a DBFunction, value and column will be passed on to 
		# the original quote method (aliased orig_quote)
		#
		# === Parameters
		# * value - the value to be quoted.
		# * column - the column this is the value for.
		#
		# === Example #1
		#	>> User.new
		#	>> user.password = ActiveRecord::Base::DBFunction.new( :password, 'secret' )
		#	>> user.save
		#	>> user.password
		#	=> "428567f408994404"
		# === Example #2
		#	>> class User < ActiveRecord::Base; def password=( pass ); super DBFunction( :password, pass ); end; end
		#	>> user = User.new
		#	>> user.password = 'secret'
		#	>> user.save
		#	>> user.password
		#	=> "428567f408994404"
		#
		########################################################################
		def quote( value, column = nil )
			if( value.is_a? ActiveRecord::Base::DBFunction )
				return value.function.to_s+'('+value.args.collect{ |a| quote(a) }.join(',')+')'
			end
			orig_quote( value, column )
		end
	end

	class Base::DBFunction
		attr_accessor :function, :args
		def initialize( function, *args )
			@function = function
			@args = args || []
		end
	end
end

