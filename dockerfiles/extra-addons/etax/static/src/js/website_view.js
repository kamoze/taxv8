function validateNumber()
{
    var trading_profile = parseFloat(document.getElementById("trading_profile").value);
    var other_profit = parseFloat(document.getElementById("other_profit").value);
     var business_income = parseFloat(document.getElementById("business_income").value);
      var professional_income = parseFloat(document.getElementById("professional_income").value);
     var salary = parseFloat(document.getElementById("salary").value);
     var fees = parseFloat(document.getElementById("fees").value);
     var commision = parseFloat(document.getElementById("commision").value);
     var benifit_in_kind = parseFloat(document.getElementById("benifit_in_kind").value);
     var bonus = parseFloat(document.getElementById("bonus").value);
     var other_income = parseFloat(document.getElementById("other_income").value);
     var gratuties = parseFloat(document.getElementById("gratuties").value);

      // for Unearned Income

      var dividiends = parseFloat(document.getElementById("dividiends").value);
      var royalities = parseFloat(document.getElementById("royalities").value);
      var interest = parseFloat(document.getElementById("interest").value);
      var other_gross = parseFloat(document.getElementById("other_gross").value);
      var rent_gross = parseFloat(document.getElementById("rent_gross").value);

      //for Satuatory Deduction


      var gratuities_sd = parseFloat(document.getElementById("gratuities_sd").value);

      var professional_body = parseFloat(document.getElementById("professional_body").value);
      var pensions_contributions = parseFloat(document.getElementById("pensions_contributions").value);
      var life_relief = parseFloat(document.getElementById("life_relief").value);
      var nhf_contributions = parseFloat(document.getElementById("nhf_contributions").value);
      var capital_allowances = parseFloat(document.getElementById("capital_allowances").value);
      var ins_superannuations = parseFloat(document.getElementById("ins_superannuations").value);
      var balancing_charges = parseFloat(document.getElementById("balancing_charges").value);
      var nhis_contributions = parseFloat(document.getElementById("nhis_contributions").value);
      var balancing_allowaces = parseFloat(document.getElementById("balancing_allowaces").value);
      var mortgage_interest = parseFloat(document.getElementById("mortgage_interest").value);
      var losses = parseFloat(document.getElementById("losses").value);

    if((trading_profile < 0) || (other_profit < 0) || (business_income < 0) || (professional_income < 0) || (salary < 0) || (fees < 0) || (commision < 0) || (benifit_in_kind < 0)
             || (bonus < 0) || (other_income < 0) || (gratuties < 0) || (dividiends < 0) || (royalities < 0) || (interest < 0) || (other_gross < 0) || (rent_gross < 0)
             || (gratuities_sd < 0) || (professional_body < 0) || (pensions_contributions < 0) || (life_relief < 0) || (nhf_contributions < 0) || (capital_allowances < 0) || (ins_superannuations < 0)
             || (balancing_charges < 0) || (nhis_contributions < 0) || (balancing_allowaces < 0) || (mortgage_interest < 0) || (losses < 0))
    {
        window.alert("please enter positive number....");
    }
}


$('#total').click(function()
{
   //Get selected data
    // for Income

     var trading_profile = parseFloat(document.getElementById("trading_profile").value);

     var other_profit = parseFloat(document.getElementById("other_profit").value);
     var business_income = parseFloat(document.getElementById("business_income").value);
     var professional_income = parseFloat(document.getElementById("professional_income").value);
     var salary = parseFloat(document.getElementById("salary").value);
     var fees = parseFloat(document.getElementById("fees").value);
     var commision = parseFloat(document.getElementById("commision").value);
     var benifit_in_kind = parseFloat(document.getElementById("benifit_in_kind").value);
     var bonus = parseFloat(document.getElementById("bonus").value);
     var other_income = parseFloat(document.getElementById("other_income").value);
     var gratuties = parseFloat(document.getElementById("gratuties").value);

     if(isNaN(trading_profile)){
            trading_profile = 0
        }
     if(isNaN(other_profit)){
            other_profit = 0
        }
     if(isNaN(business_income)){
            business_income = 0
        }
     if(isNaN(professional_income)){
            professional_income = 0
        }
     if(isNaN(salary)){
            salary = 0
        }
     if(isNaN(fees)){
            fees = 0
        }
     if(isNaN(commision)){
            commision = 0
        }
     if(isNaN(benifit_in_kind)){
            benifit_in_kind = 0
        }
     if(isNaN(bonus)){
            bonus = 0
        }
     if(isNaN(other_income)){
            other_income = 0
        }
     if(isNaN(gratuties)){
            gratuties = 0
        }

      //calculate total value
      var inc = trading_profile+other_profit+business_income+professional_income+salary+fees+commision+benifit_in_kind+bonus+other_income+gratuties;



      // for Unearned Income

      var dividiends = parseFloat(document.getElementById("dividiends").value);
      var royalities = parseFloat(document.getElementById("royalities").value);
      var interest = parseFloat(document.getElementById("interest").value);
      var other_gross = parseFloat(document.getElementById("other_gross").value);
      var rent_gross = parseFloat(document.getElementById("rent_gross").value);

       if(isNaN(dividiends)){
            dividiends = 0
        }
       if(isNaN(royalities)){
            royalities = 0
        }
       if(isNaN(interest)){
            interest = 0
        }
       if(isNaN(other_gross)){
            other_gross = 0
        }
       if(isNaN(rent_gross)){
            rent_gross = 0
        }

      var unearned_income = dividiends+royalities+interest+other_gross+rent_gross


      // Tax Summary

      var total_amt = parseFloat(document.getElementById("total_amt").value);
      var tax_liability = parseFloat(document.getElementById("tax_liability").value);
      var consolidated = parseFloat(document.getElementById("consolidated").value);
      var total_relief = parseFloat(document.getElementById("total_relief").value);
      var next_taxable_inc = parseFloat(document.getElementById("next_taxable_inc").value);


      var tax_sumary = total_amt+tax_liability+consolidated+total_relief+next_taxable_inc

      //for Satuatory Deduction


      var gratuities_sd = parseFloat(document.getElementById("gratuities_sd").value);

      var professional_body = parseFloat(document.getElementById("professional_body").value);
      var pensions_contributions = parseFloat(document.getElementById("pensions_contributions").value);
      var life_relief = parseFloat(document.getElementById("life_relief").value);
      var nhf_contributions = parseFloat(document.getElementById("nhf_contributions").value);
      var capital_allowances = parseFloat(document.getElementById("capital_allowances").value);
      var ins_superannuations = parseFloat(document.getElementById("ins_superannuations").value);
      var balancing_charges = parseFloat(document.getElementById("balancing_charges").value);
      var nhis_contributions = parseFloat(document.getElementById("nhis_contributions").value);
      var balancing_allowaces = parseFloat(document.getElementById("balancing_allowaces").value);
      var mortgage_interest = parseFloat(document.getElementById("mortgage_interest").value);
      var losses = parseFloat(document.getElementById("losses").value);

       if(isNaN(gratuities_sd)){
            gratuities_sd = 0
        }
       if(isNaN(professional_body)){
            professional_body = 0
        }
       if(isNaN(pensions_contributions)){
            pensions_contributions = 0
        }
       if(isNaN(life_relief)){
            life_relief = 0
        }
       if(isNaN(nhf_contributions)){
            nhf_contributions = 0
        }
       if(isNaN(capital_allowances)){
            capital_allowances = 0
        }
       if(isNaN(ins_superannuations)){
            ins_superannuations = 0
        }
       if(isNaN(balancing_charges)){
            balancing_charges = 0
        }
       if(isNaN(nhis_contributions)){
            nhis_contributions = 0
        }
       if(isNaN(balancing_allowaces)){
            balancing_allowaces = 0
        }
       if(isNaN(mortgage_interest)){
            mortgage_interest = 0
        }
       if(isNaN(losses)){
            losses = 0
        }

      var sd = gratuities_sd+professional_body+pensions_contributions+life_relief+nhf_contributions+ins_superannuations+balancing_charges+nhis_contributions+balancing_allowaces+losses+capital_allowances+mortgage_interest


      // totals

      var total_amount = inc+unearned_income

      //print value to  PicExtPrice
      document.getElementById("total_amt").value=total_amount;










      // calculate ta
      var div = dividiends+interest;

      var ta=(total_amount-div);
    //Consolidated Relief


      var tal=0.0

      if (total_amount <= 250000)
      {


            document.getElementById("consolidated").value=0.0;

      }
      else if (total_amount > 250000){
            var per= ta * 0.01
            var tota2 = ta * 0.2

            if (per < 200000)
            {
                Math.round(ta1=200000 + tota2);
                document.getElementById("consolidated").value=ta1;
            }
            else{
                Math.round(ta1=per + tota2);
                document.getElementById("consolidated").value=ta1;

            }
      }
      else
        {
            Math.round(ta1=ta*0.01);
            document.getElementById("consolidated").value=ta1;
        }


    // Total Refief

     var sd = gratuities_sd+professional_body+pensions_contributions+life_relief+nhf_contributions+ins_superannuations+balancing_charges+nhis_contributions+balancing_allowaces+losses+capital_allowances+mortgage_interest


     if (consolidated<250000)

     {
        document.getElementById("total_relief").value=0.0;
     }
     else
      {
        document.getElementById("total_relief").value=consolidated + sd;
      }

    // net taxable income

     taxable_income=0.0;


     Math.round(taxable_income = total_amt - total_relief);

     document.getElementById("next_taxable_inc").value=taxable_income;



 //Tax Liability

    tax_liability = 0.0
    if ((total_amt > 0) && (total_amt <= 300000)) {


            tax_liability=0.01*total_amt;
     }



    else if ((next_taxable_inc > 0) && (next_taxable_inc <= 300000))
    {
         tax_liability=0.07*next_taxable_inc;

    }
    else if ((next_taxable_inc >  300000) && (next_taxable_inc <= 600000))
    {
        tax_liability=21000+0.11*(next_taxable_inc-300000);
    }
    else if ((next_taxable_inc >  600000) && (next_taxable_inc <= 1100000))
    {
        tax_liability=54000+0.15*(next_taxable_inc-600000);
    }
    else if ((next_taxable_inc >  1100000) && (next_taxable_inc <= 1600000))
    {
         tax_liability=129000+0.19*(next_taxable_inc-1100000);
    }
    else if ((next_taxable_inc >  1600000) && (next_taxable_inc <= 3200000))
    {
        tax_liability=224000+0.21*(next_taxable_inc-1600000);
    }
    else if (next_taxable_inc >  3200000)
    {
        tax_liability=560000+0.24*(next_taxable_inc-3200000);
    }

    document.getElementById("tax_liability").value=Math.round(tax_liability);





});