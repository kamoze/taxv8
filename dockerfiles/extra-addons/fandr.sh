#!/bin/bash
     for fl in openeducat_ext/application/mail_template/*.xml; do
     mv $fl $fl.old
     sed 's/Demo CollegeL/Demo College/g' $fl.old > $fl
     rm -f $fl.old
     done
