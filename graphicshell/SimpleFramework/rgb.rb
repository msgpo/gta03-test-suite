#!/usr/bin/env ruby
# COPYRIGHT: Openmoko Inc. 2009
# LICENSE: GPL Version 2 or later
# DESCRIPTION: convert the X11 rgp.txt to a Python file
# AUTHOR: Christopher Hall <hsw@openmoko.com>

xorg_rgb = '/etc/X11/rgb.txt'

colours = {}

print "# derived from: ", xorg_rgb, "\n"
File.open(xorg_rgb, "r").readlines.each do |l|
  l.chomp!()
  if l =~/^[[:space:]]*([[:digit:]]+)[[:space:]]+([[:digit:]]+)[[:space:]]+([[:digit:]]+)[[:space:]]+([[:alnum:]]+)[[:space:]]*$/ then
    rgb = [$1, $2, $3]
    name = $4
    colours[name] = rgb
  elsif l =~/^[[:space:]]*![[:space:]]*([^[:space:]].*[^[:space:]])[[:space:]]*$/ then
    print "# ", $1, "\n"
  end
end

# sort into this order: word word0 word1 ... word10 word11 ... word 99 word 100
def compare(x, y)
  rx = /^([[:alpha:]]+)([[:digit:]]*)$/.match(x[0])
  ry = /^([[:alpha:]]+)([[:digit:]]*)$/.match(y[0]) 
  key1 = rx[1]
  key2 = ry[1]
  num1 = if rx[2] then rx[2].to_i() else -1 end
  num2 = if ry[2] then ry[2].to_i() else -1 end
  result = key1.casecmp(key2)
  if result == 0 then
    num1 <=> num2
  else
    result
  end
end

print "\nclass Colour:\n"
colours.sort{|x,y| compare(x, y)}.each do |name, rgb|
  print "    ", name, " = ", rgb.join(', '), "\n"
end
print "# End\n"
